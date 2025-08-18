from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, UpdateView, ListView, DetailView
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import CustomUser, Profile
from .forms import CustomUserCreationForm, ProfileForm, CustomLoginForm

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.role == 'chairman':
            return reverse_lazy('gc_requests:chairman_dashboard')
        elif user.role == 'councilor':
            return reverse_lazy('gc_requests:councilor_dashboard')
        elif user.role == 'labour':
            return reverse_lazy('gc_requests:labour_dashboard')
        else:
            return reverse_lazy('gc_requests:user_dashboard')

class CustomLogoutView(View):
    """Custom logout view that handles both GET and POST requests"""
    
    def get(self, request):
        return self.logout_user(request)
    
    def post(self, request):
        return self.logout_user(request)
    
    def logout_user(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('/')  # Redirect to home page

class SignupView(View):
    template_name = 'accounts/signup.html'
    
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                # Create profile
                Profile.objects.create(
                    user=user,
                    first_name=form.cleaned_data.get('first_name'),
                    middle_name=form.cleaned_data.get('middle_name'),
                    last_name=form.cleaned_data.get('last_name'),
                    address=form.cleaned_data.get('address'),
                    landmark=form.cleaned_data.get('landmark'),
                )
                
                # Log the user in
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, 'Account created successfully!')
                    return redirect('gc_requests:user_dashboard')
        
        return render(request, self.template_name, {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            context['profile'] = user.profile
        except Profile.DoesNotExist:
            context['profile'] = None
        
        # Add request statistics
        if hasattr(user, 'requests'):
            all_requests = user.requests.all()
            active_statuses = ['pending', 'assigned', 'in_progress']
            
            context['total_requests'] = all_requests.count()
            context['active_requests'] = all_requests.filter(status__in=active_statuses).count()
            context['completed_requests'] = all_requests.filter(status='approved').count()
            
            # Calculate success rate
            if context['total_requests'] > 0:
                context['success_rate'] = round((context['completed_requests'] / context['total_requests']) * 100, 1)
            else:
                context['success_rate'] = 0
        else:
            context['total_requests'] = 0
            context['active_requests'] = 0
            context['completed_requests'] = 0
            context['success_rate'] = 0
            
        return context

class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_edit.html'
    
    def get(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile(user=request.user)
        
        # Create forms with initial data
        profile_form = ProfileForm(instance=profile)
        user_form_data = {
            'username': request.user.username,
            'email': request.user.email or '',
            'phone_number': request.user.phone_number,
            'ward_number': request.user.ward_number or '',
        }
        
        return render(request, self.template_name, {
            'form': profile_form,
            'user_form_data': user_form_data
        })
    
    def post(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile(user=request.user)
        
        # Handle profile form
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        # Handle user data updates
        user = request.user
        user_updated = False
        errors = []
        
        # Update user fields if provided
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip()
        new_phone = request.POST.get('phone_number', '').strip()
        new_ward = request.POST.get('ward_number', '').strip()
        
        if new_username and new_username != user.username:
            if CustomUser.objects.filter(username=new_username).exclude(id=user.id).exists():
                errors.append('Username already taken.')
            else:
                user.username = new_username
                user_updated = True
        
        if new_phone and new_phone != user.phone_number:
            if CustomUser.objects.filter(phone_number=new_phone).exclude(id=user.id).exists():
                errors.append('Phone number already registered.')
            else:
                user.phone_number = new_phone
                user_updated = True
        
        if new_email != (user.email or ''):
            user.email = new_email if new_email else None
            user_updated = True
        
        if new_ward != str(user.ward_number or ''):
            user.ward_number = int(new_ward) if new_ward else None
            user_updated = True
        
        # Validate and save
        if profile_form.is_valid() and not errors:
            profile_form.save()
            if user_updated:
                user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            if errors:
                for error in errors:
                    messages.error(request, error)
        
        # Re-render with data
        user_form_data = {
            'username': new_username or user.username,
            'email': new_email or user.email or '',
            'phone_number': new_phone or user.phone_number,
            'ward_number': new_ward or user.ward_number or '',
        }
        
        return render(request, self.template_name, {
            'form': profile_form,
            'user_form_data': user_form_data
        })

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class UserManagementView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'accounts/user_management.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role in ['chairman', 'councilor']
    
    def get_queryset(self):
        queryset = CustomUser.objects.select_related('profile').all()
        if self.request.user.role == 'councilor':
            # Councilors can only manage users in their ward
            queryset = queryset.filter(ward_number=self.request.user.ward_number)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        # Role filter
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Ward filter (only for chairman)
        ward = self.request.GET.get('ward')
        if ward and self.request.user.role == 'chairman':
            queryset = queryset.filter(ward_number=ward)
        
        return queryset.order_by('-date_joined')

class UserEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'accounts/user_edit.html'
    
    def test_func(self):
        return self.request.user.role in ['chairman', 'councilor']
    
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        if request.user.role == 'councilor' and user.ward_number != request.user.ward_number:
            messages.error(request, 'You can only edit users in your ward.')
            return redirect('accounts:user_management')
        
        return render(request, self.template_name, {'edit_user': user})
    
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        if request.user.role == 'councilor' and user.ward_number != request.user.ward_number:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Handle user updates (role changes, ward assignments, etc.)
        if request.user.role == 'chairman':
            user.role = request.POST.get('role', user.role)
            user.ward_number = request.POST.get('ward_number') or user.ward_number
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()
            messages.success(request, 'User updated successfully!')
        
        return redirect('accounts:user_management')

class ProfileViewUser(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/profile_view.html'
    context_object_name = 'profile_user'
    pk_url_kwarg = 'user_id'
    
    def test_func(self):
        return self.request.user.role in ['chairman', 'councilor']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        
        # Check permission for councilor
        if self.request.user.role == 'councilor' and profile_user.ward_number != self.request.user.ward_number:
            raise PermissionDenied("You can only view profiles in your ward")
        
        # Add user statistics
        from gc_requests.models import GarbageRequest
        if hasattr(profile_user, 'profile'):
            context['total_requests'] = GarbageRequest.objects.filter(user=profile_user).count()
            context['completed_requests'] = GarbageRequest.objects.filter(user=profile_user, status='completed').count()
            context['pending_requests'] = GarbageRequest.objects.filter(user=profile_user, status='pending').count()
            context['in_progress_requests'] = GarbageRequest.objects.filter(user=profile_user, status='in_progress').count()
            
        return context
