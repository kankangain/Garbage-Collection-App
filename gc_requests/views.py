from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import GarbageRequest, CompletionReport, RequestTracking
from accounts.forms import GarbageRequestForm
from accounts.models import CustomUser
from notifications.models import Notification

# User Views
class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'gc_requests/user_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_requests = GarbageRequest.objects.filter(user=self.request.user)
        
        context.update({
            'total_requests': user_requests.count(),
            'pending_requests': user_requests.filter(status__in=['pending', 'assigned', 'in_progress']).count(),
            'completed_requests': user_requests.filter(status='approved').count(),
            'recent_requests': user_requests[:5],
        })
        return context

class CreateRequestView(LoginRequiredMixin, View):
    template_name = 'gc_requests/create_request.html'
    
    def get(self, request):
        # Pre-fill form with user's profile data if available
        initial_data = {}
        try:
            profile = request.user.profile
            initial_data = {
                'first_name': profile.first_name,
                'middle_name': profile.middle_name,
                'last_name': profile.last_name,
                'address': profile.address,
                'landmark': profile.landmark,
                'phone_number': request.user.phone_number,
                'email': request.user.email,
            }
        except:
            pass
        
        form = GarbageRequestForm(initial=initial_data)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = GarbageRequestForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                # Create garbage request
                garbage_request = GarbageRequest.objects.create(
                    user=request.user,
                    first_name=form.cleaned_data['first_name'],
                    middle_name=form.cleaned_data['middle_name'],
                    last_name=form.cleaned_data['last_name'],
                    address=form.cleaned_data['address'],
                    landmark=form.cleaned_data['landmark'],
                    ward_number=int(form.cleaned_data['ward_number']),
                    phone_number=form.cleaned_data['phone_number'],
                    email=form.cleaned_data['email'],
                    category=form.cleaned_data['category'],
                    garbage_image=form.cleaned_data['garbage_image'],
                    description=form.cleaned_data['description'],
                )
                
                # Create tracking entry
                RequestTracking.objects.create(
                    request=garbage_request,
                    action='created',
                    user=request.user,
                    notes=f"Request created for {garbage_request.get_category_display()}"
                )
                
                # Send notification to councilor
                councilor = CustomUser.objects.filter(
                    role='councilor',
                    ward_number=garbage_request.ward_number
                ).first()
                
                if councilor:
                    Notification.objects.create(
                        recipient=councilor,
                        title='New Garbage Collection Request',
                        message=f'New {garbage_request.get_category_display()} request in Ward {garbage_request.ward_number}',
                        notification_type='request_created',
                        request=garbage_request
                    )
                
                messages.success(request, 'Your garbage collection request has been submitted successfully!')
                return redirect('gc_requests:request_detail', request_id=garbage_request.id)
        
        return render(request, self.template_name, {'form': form})

class MyRequestsView(LoginRequiredMixin, ListView):
    template_name = 'gc_requests/my_requests.html'
    context_object_name = 'requests'
    paginate_by = 10
    
    def get_queryset(self):
        return GarbageRequest.objects.filter(user=self.request.user).order_by('-created_at')

class RequestDetailView(LoginRequiredMixin, DetailView):
    model = GarbageRequest
    template_name = 'gc_requests/request_detail.html'
    context_object_name = 'request'
    pk_url_kwarg = 'request_id'
    
    def get_object(self):
        request_obj = get_object_or_404(GarbageRequest, id=self.kwargs['request_id'])
        # Users can only view their own requests (unless they're staff)
        if request_obj.user != self.request.user and self.request.user.role == 'user':
            raise Http404
        return request_obj

class TrackRequestView(LoginRequiredMixin, DetailView):
    model = GarbageRequest
    template_name = 'gc_requests/track_request.html'
    context_object_name = 'request'
    pk_url_kwarg = 'request_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_history'] = self.object.tracking.all()
        context['completion_reports'] = self.object.completion_reports.all()
        return context

# Labour Views
class LabourDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gc_requests/labour_dashboard.html'
    
    def test_func(self):
        return self.request.user.role == 'labour'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        labour_requests = GarbageRequest.objects.filter(assigned_labour=self.request.user)
        
        context.update({
            'assigned_requests': labour_requests.filter(status='assigned').count(),
            'in_progress_requests': labour_requests.filter(status='in_progress').count(),
            'completed_requests': labour_requests.filter(status='approved').count(),
            'overdue_requests': [req for req in labour_requests if req.is_overdue],
            'recent_requests': labour_requests.filter(status__in=['assigned', 'in_progress'])[:5],
        })
        return context

class LabourRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'gc_requests/labour_requests.html'
    context_object_name = 'requests'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.role == 'labour'
    
    def get_queryset(self):
        return GarbageRequest.objects.filter(
            assigned_labour=self.request.user
        ).order_by('-assigned_at')

class LabourRequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = GarbageRequest
    template_name = 'gc_requests/labour_request_detail.html'
    context_object_name = 'request'
    pk_url_kwarg = 'request_id'
    
    def test_func(self):
        return self.request.user.role == 'labour'

class StartWorkView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'labour'
    
    def post(self, request, request_id):
        garbage_request = get_object_or_404(
            GarbageRequest,
            id=request_id,
            assigned_labour=request.user,
            status='assigned'
        )
        
        garbage_request.status = 'in_progress'
        garbage_request.save()
        
        # Create tracking entry
        RequestTracking.objects.create(
            request=garbage_request,
            action='in_progress',
            user=request.user,
            notes='Work started by labour'
        )
        
        messages.success(request, 'Work status updated to In Progress.')
        return redirect('gc_requests:labour_request_detail', request_id=request_id)

class CompleteWorkView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'gc_requests/complete_work.html'
    
    def test_func(self):
        return self.request.user.role == 'labour'
    
    def get(self, request, request_id):
        garbage_request = get_object_or_404(
            GarbageRequest,
            id=request_id,
            assigned_labour=request.user,
            status='in_progress'
        )
        return render(request, self.template_name, {'request': garbage_request})
    
    def post(self, request, request_id):
        garbage_request = get_object_or_404(
            GarbageRequest,
            id=request_id,
            assigned_labour=request.user,
            status='in_progress'
        )
        
        completion_image = request.FILES.get('completion_image')
        notes = request.POST.get('notes', '')
        
        if completion_image:
            with transaction.atomic():
                # Create completion report
                completion_report = CompletionReport.objects.create(
                    request=garbage_request,
                    labour=request.user,
                    completion_image=completion_image,
                    notes=notes
                )
                
                garbage_request.status = 'completed'
                garbage_request.completed_at = timezone.now()
                garbage_request.save()
                
                # Create tracking entry
                RequestTracking.objects.create(
                    request=garbage_request,
                    action='completed',
                    user=request.user,
                    notes='Work completed by labour'
                )
                
                # Notify councilor
                councilor = CustomUser.objects.filter(
                    role='councilor',
                    ward_number=garbage_request.ward_number
                ).first()
                
                if councilor:
                    Notification.objects.create(
                        recipient=councilor,
                        title='Work Completed',
                        message=f'Request #{garbage_request.id} has been completed and needs approval',
                        notification_type='work_completed',
                        request=garbage_request
                    )
                
                messages.success(request, 'Work completion report submitted successfully!')
                return redirect('gc_requests:labour_request_detail', request_id=request_id)
        else:
            messages.error(request, 'Please upload a completion image.')
            return render(request, self.template_name, {'request': garbage_request})

# Councilor Views
class CouncilorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gc_requests/councilor_dashboard.html'
    
    def test_func(self):
        return self.request.user.role == 'councilor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ward_requests = GarbageRequest.objects.filter(ward_number=self.request.user.ward_number)
        
        context.update({
            'ward_number': self.request.user.ward_number,
            'pending_requests': ward_requests.filter(status='pending').count(),
            'in_progress_requests': ward_requests.filter(status__in=['assigned', 'in_progress']).count(),
            'completed_requests': ward_requests.filter(status='approved').count(),
            'pending_approvals': ward_requests.filter(status='completed').count(),
            'recent_requests': ward_requests.order_by('-created_at')[:5],
        })
        return context

class CouncilorRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'gc_requests/councilor_requests.html'
    context_object_name = 'requests'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.role == 'councilor'
    
    def get_queryset(self):
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        queryset = GarbageRequest.objects.filter(
            ward_number=self.request.user.ward_number
        )
        
        # Apply filters based on GET parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        date_range = self.request.GET.get('date_range')
        if date_range:
            now = timezone.now()
            if date_range == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(created_at__gte=start_date)
            elif date_range == 'week':
                start_date = now - timedelta(days=7)
                queryset = queryset.filter(created_at__gte=start_date)
            elif date_range == 'month':
                start_date = now - timedelta(days=30)
                queryset = queryset.filter(created_at__gte=start_date)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all requests for this ward for statistics
        ward_requests = GarbageRequest.objects.filter(ward_number=self.request.user.ward_number)
        
        # Calculate statistics
        context.update({
            'total_requests': ward_requests.count(),
            'pending_requests': ward_requests.filter(status='pending').count(),
            'active_requests': ward_requests.filter(status__in=['assigned', 'in_progress']).count(),
            'completed_requests': ward_requests.filter(status='approved').count(),
            'overdue_requests': sum(1 for req in ward_requests if req.is_overdue),
        })
        
        return context

class AssignRequestView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'councilor'
    
    def post(self, request, request_id):
        garbage_request = get_object_or_404(
            GarbageRequest,
            id=request_id,
            ward_number=request.user.ward_number,
            status='pending'
        )
        
        labour_id = request.POST.get('labour_id')
        labour = get_object_or_404(
            CustomUser,
            id=labour_id,
            role='labour',
            ward_number=request.user.ward_number
        )
        
        with transaction.atomic():
            garbage_request.assigned_labour = labour
            garbage_request.status = 'assigned'
            garbage_request.assigned_at = timezone.now()
            garbage_request.save()
            
            # Create tracking entry
            RequestTracking.objects.create(
                request=garbage_request,
                action='assigned',
                user=request.user,
                notes=f'Assigned to {labour.profile.full_name if hasattr(labour, "profile") else labour.username}'
            )
            
            # Notify labour
            Notification.objects.create(
                recipient=labour,
                title='New Assignment',
                message=f'You have been assigned request #{garbage_request.id}',
                notification_type='request_assigned',
                request=garbage_request
            )
        
        messages.success(request, f'Request assigned to {labour.username} successfully!')
        return redirect('gc_requests:councilor_requests')

class CouncilorReportsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'gc_requests/councilor_reports.html'
    context_object_name = 'reports'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.role == 'councilor'
    
    def get_queryset(self):
        return CompletionReport.objects.filter(
            request__ward_number=self.request.user.ward_number,
            status='submitted'
        ).order_by('-submitted_at')

class ApproveReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'councilor'
    
    def post(self, request, report_id):
        completion_report = get_object_or_404(
            CompletionReport,
            id=report_id,
            request__ward_number=request.user.ward_number,
            status='submitted'
        )
        
        with transaction.atomic():
            completion_report.status = 'approved'
            completion_report.reviewed_at = timezone.now()
            completion_report.reviewed_by = request.user
            completion_report.save()
            
            completion_report.request.status = 'approved'
            completion_report.request.approved_at = timezone.now()
            completion_report.request.save()
            
            # Create tracking entry
            RequestTracking.objects.create(
                request=completion_report.request,
                action='report_approved',
                user=request.user,
                notes='Completion report approved by councilor'
            )
            
            # Notify user
            Notification.objects.create(
                recipient=completion_report.request.user,
                title='Request Completed',
                message=f'Your request #{completion_report.request.id} has been completed successfully!',
                notification_type='report_approved',
                request=completion_report.request
            )
        
        messages.success(request, 'Completion report approved successfully!')
        return redirect('gc_requests:councilor_reports')

class RejectReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, report_id):
        completion_report = get_object_or_404(
            CompletionReport,
            id=report_id,
            request__ward_number=request.user.ward_number,
            status='submitted'
        )
        
        rejection_reason = request.POST.get('rejection_reason', '')
        
        with transaction.atomic():
            completion_report.status = 'rejected'
            completion_report.reviewed_at = timezone.now()
            completion_report.reviewed_by = request.user
            completion_report.rejection_reason = rejection_reason
            completion_report.save()
            
            completion_report.request.status = 'in_progress'
            completion_report.request.save()
            
            # Create tracking entry
            RequestTracking.objects.create(
                request=completion_report.request,
                action='report_rejected',
                user=request.user,
                notes=f'Completion report rejected: {rejection_reason}'
            )
            
            # Notify labour
            Notification.objects.create(
                recipient=completion_report.labour,
                title='Report Rejected',
                message=f'Your completion report for request #{completion_report.request.id} was rejected. Reason: {rejection_reason}',
                notification_type='report_rejected',
                request=completion_report.request
            )
        
        messages.success(request, 'Completion report rejected. Labour has been notified.')
        return redirect('gc_requests:councilor_reports')

# Chairman Views
class ChairmanDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gc_requests/chairman_dashboard.html'
    
    def test_func(self):
        return self.request.user.role == 'chairman'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_requests = GarbageRequest.objects.all()
        
        # Ward-wise statistics
        ward_stats = {}
        for ward in range(1, 21):
            ward_requests = all_requests.filter(ward_number=ward)
            ward_stats[ward] = {
                'total': ward_requests.count(),
                'pending': ward_requests.filter(status='pending').count(),
                'in_progress': ward_requests.filter(status__in=['assigned', 'in_progress']).count(),
                'completed': ward_requests.filter(status='approved').count(),
                'overdue': len([req for req in ward_requests if req.is_overdue])
            }
        
        context.update({
            'total_requests': all_requests.count(),
            'pending_requests': all_requests.filter(status='pending').count(),
            'in_progress_requests': all_requests.filter(status__in=['assigned', 'in_progress']).count(),
            'completed_requests': all_requests.filter(status='approved').count(),
            'overdue_requests': len([req for req in all_requests if req.is_overdue]),
            'ward_stats': ward_stats,
            'recent_requests': all_requests.order_by('-created_at')[:10],
        })
        return context

class ChairmanRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'gc_requests/chairman_requests.html'
    context_object_name = 'requests'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role == 'chairman'
    
    def get_queryset(self):
        queryset = GarbageRequest.objects.all().order_by('-created_at')
        
        # Filter by ward if specified
        ward_filter = self.request.GET.get('ward')
        if ward_filter:
            queryset = queryset.filter(ward_number=ward_filter)
        
        # Filter by status if specified
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ward_choices'] = [(i, f'Ward {i}') for i in range(1, 21)]
        context['status_choices'] = GarbageRequest.STATUS_CHOICES
        context['current_ward'] = self.request.GET.get('ward')
        context['current_status'] = self.request.GET.get('status')
        return context

class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gc_requests/analytics.html'
    
    def test_func(self):
        return self.request.user.role == 'chairman'
    
    def get_context_data(self, **kwargs):
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        context = super().get_context_data(**kwargs)
        
        # Generate analytics data
        all_requests = GarbageRequest.objects.all()
        now = timezone.now()
        
        # Basic metrics
        total_requests = all_requests.count()
        completed_requests = all_requests.filter(status='approved').count()
        pending_requests = all_requests.filter(status='pending').count()
        in_progress_requests = all_requests.filter(status__in=['assigned', 'in_progress']).count()
        
        # Calculate overdue requests
        overdue_requests = len([req for req in all_requests.filter(
            status__in=['assigned', 'in_progress']
        ) if req.is_overdue])
        
        # Completion rate
        completion_rate = round((completed_requests / total_requests * 100) if total_requests > 0 else 0, 1)
        
        # Monthly requests
        thirty_days_ago = now - timedelta(days=30)
        monthly_requests = all_requests.filter(created_at__gte=thirty_days_ago).count()
        
        # Category-wise breakdown
        category_stats = {}
        for category_code, category_name in GarbageRequest.GARBAGE_CATEGORIES:
            count = all_requests.filter(category=category_code).count()
            category_stats[category_name] = count
        
        # Ward statistics
        ward_stats = []
        for ward_num in range(1, 21):
            ward_requests = all_requests.filter(ward_number=ward_num)
            ward_total = ward_requests.count()
            
            if ward_total > 0:
                ward_completed = ward_requests.filter(status='approved').count()
                ward_in_progress = ward_requests.filter(status__in=['assigned', 'in_progress']).count()
                ward_pending = ward_requests.filter(status='pending').count()
                ward_overdue = len([req for req in ward_requests.filter(
                    status__in=['assigned', 'in_progress']
                ) if req.is_overdue])
                
                # Get councilor for this ward
                from accounts.models import CustomUser
                councilor = CustomUser.objects.filter(role='councilor', ward_number=ward_num).first()
                
                ward_stats.append({
                    'ward_number': ward_num,
                    'total_requests': ward_total,
                    'completed_requests': ward_completed,
                    'in_progress_requests': ward_in_progress,
                    'pending_requests': ward_pending,
                    'overdue_requests': ward_overdue,
                    'completed_percentage': round((ward_completed / ward_total * 100), 1),
                    'in_progress_percentage': round((ward_in_progress / ward_total * 100), 1),
                    'pending_percentage': round((ward_pending / ward_total * 100), 1),
                    'overdue_percentage': round((ward_overdue / ward_total * 100), 1),
                    'councilor': councilor
                })
        
        # Sort by total requests descending
        ward_stats.sort(key=lambda x: x['total_requests'], reverse=True)
        
        # Recent activities (last 10) - ordered by most recent creation
        recent_activities = all_requests.select_related('user', 'assigned_labour').order_by('-created_at')[:10]
        
        # Trends data for last 30 days
        trends_data = defaultdict(lambda: {'submitted': 0, 'completed': 0})
        
        # Get data for last 30 days
        for i in range(30):
            date = (now - timedelta(days=i)).date()
            submitted_count = all_requests.filter(created_at__date=date).count()
            completed_count = all_requests.filter(approved_at__date=date).count()
            
            trends_data[date.strftime('%m-%d')] = {
                'submitted': submitted_count,
                'completed': completed_count
            }
        
        # Prepare chart data
        sorted_dates = sorted(trends_data.keys())
        trends_labels = sorted_dates
        trends_submitted = [trends_data[date]['submitted'] for date in sorted_dates]
        trends_completed = [trends_data[date]['completed'] for date in sorted_dates]
        
        # System alerts
        system_alerts = []
        
        # High workload alerts
        high_workload_wards = [w for w in ward_stats if w['pending_requests'] > 5]
        for ward in high_workload_wards:
            system_alerts.append({
                'type': 'warning',
                'icon': 'exclamation-triangle',
                'title': f'High Workload - Ward {ward["ward_number"]}',
                'message': f'{ward["pending_requests"]} pending requests require attention.',
                'action_url': f'/requests/ward/{ward["ward_number"]}/',
                'action_text': 'View Ward Details'
            })
        
        # Labour capacity alerts
        from accounts.models import CustomUser
        total_labour = CustomUser.objects.filter(role='labour').count()
        active_requests = in_progress_requests + pending_requests
        
        if total_labour > 0 and (active_requests / total_labour) > 5:
            system_alerts.append({
                'type': 'warning',
                'icon': 'people',
                'title': 'Labour Capacity Alert',
                'message': f'High requests-to-labour ratio: {round(active_requests/total_labour, 1)}:1',
                'action_url': '/admin/accounts/customuser/',
                'action_text': 'Manage Labour'
            })
        
        context.update({
            'category_stats': category_stats,
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'pending_requests': pending_requests,
            'in_progress_requests': in_progress_requests,
            'overdue_requests': overdue_requests,
            'completion_rate': completion_rate,
            'monthly_requests': monthly_requests,
            'ward_stats': ward_stats,
            'recent_activities': recent_activities,
            'trends_labels': trends_labels,
            'trends_submitted': trends_submitted,
            'trends_completed': trends_completed,
            'system_alerts': system_alerts,
        })
        
        return context

class OverdueRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'gc_requests/overdue_requests.html'
    context_object_name = 'requests'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role == 'chairman'
    
    def get_queryset(self):
        all_requests = GarbageRequest.objects.filter(
            status__in=['assigned', 'in_progress']
        ).select_related('assigned_labour', 'user')
        
        # Filter overdue requests
        overdue_requests = [req for req in all_requests if req.is_overdue]
        return overdue_requests

# API Views
class AvailableLabourAPIView(LoginRequiredMixin, View):
    def get(self, request):
        # Only councilors can access this
        if request.user.role != 'councilor':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get labour workers in the same ward as the councilor
        labour_workers = CustomUser.objects.filter(
            role='labour',
            ward_number=request.user.ward_number,
            is_active=True
        )
        
        # Build response data with active request counts
        labour_data = []
        for worker in labour_workers:
            active_requests = GarbageRequest.objects.filter(
                assigned_labour=worker,
                status__in=['assigned', 'in_progress']
            ).count()
            
            # Get worker's full name
            try:
                full_name = worker.profile.full_name if hasattr(worker, 'profile') else worker.username
            except:
                full_name = worker.username
            
            labour_data.append({
                'id': worker.id,
                'name': full_name,
                'username': worker.username,
                'phone_number': worker.phone_number,
                'active_requests': active_requests
            })
        
        return JsonResponse({
            'labour_workers': labour_data,
            'ward_number': request.user.ward_number
        })

class WardStatisticsAPIView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role not in ['chairman', 'councilor']:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        ward_number = request.GET.get('ward')
        if not ward_number:
            return JsonResponse({'error': 'Ward number required'}, status=400)
        
        ward_requests = GarbageRequest.objects.filter(ward_number=ward_number)
        
        stats = {
            'total': ward_requests.count(),
            'pending': ward_requests.filter(status='pending').count(),
            'in_progress': ward_requests.filter(status__in=['assigned', 'in_progress']).count(),
            'completed': ward_requests.filter(status='approved').count(),
        }
        
        return JsonResponse(stats)

class RequestLocationAPIView(LoginRequiredMixin, View):
    def get(self, request, request_id):
        garbage_request = get_object_or_404(GarbageRequest, id=request_id)
        
        # Check permissions
        if (request.user.role == 'user' and garbage_request.user != request.user) or \
           (request.user.role == 'councilor' and garbage_request.ward_number != request.user.ward_number) or \
           (request.user.role == 'labour' and garbage_request.assigned_labour != request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        return JsonResponse({
            'latitude': garbage_request.latitude,
            'longitude': garbage_request.longitude,
            'address': garbage_request.address,
            'landmark': garbage_request.landmark,
        })


class CancelRequestAPIView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        garbage_request = get_object_or_404(GarbageRequest, id=request_id)
        
        # Check permissions - only the user who created the request can cancel it
        if garbage_request.user != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        # Check if request can be cancelled (only pending or assigned requests can be cancelled)
        if garbage_request.status not in ['pending', 'assigned']:
            return JsonResponse({
                'success': False, 
                'error': f'Cannot cancel request with status: {garbage_request.get_status_display()}'
            }, status=400)
        
        try:
            # Update request status to cancelled
            garbage_request.status = 'cancelled'
            garbage_request.save()
            
            # Create notification for assigned labour if exists
            if garbage_request.assigned_labour:
                from notifications.models import Notification
                Notification.objects.create(
                    user=garbage_request.assigned_labour,
                    title='Request Cancelled',
                    message=f'Request #{garbage_request.id} has been cancelled by the user.',
                    request=garbage_request,
                    type='request_cancelled'
                )
            
            return JsonResponse({'success': True, 'message': 'Request cancelled successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
