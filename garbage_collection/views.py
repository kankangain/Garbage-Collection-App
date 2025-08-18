from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from gc_requests.models import GarbageRequest

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        # Redirect based on user role
        if request.user.role == 'chairman':
            return redirect('gc_requests:chairman_dashboard')
        elif request.user.role == 'councilor':
            return redirect('gc_requests:councilor_dashboard')
        elif request.user.role == 'labour':
            return redirect('gc_requests:labour_dashboard')
        else:
            return redirect('gc_requests:user_dashboard')
    
    # Show public landing page
    context = {
        'total_requests': GarbageRequest.objects.count(),
        'completed_requests': GarbageRequest.objects.filter(status='approved').count(),
    }
    return render(request, 'home.html', context)
