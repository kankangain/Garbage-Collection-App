from django.urls import path
from . import views

app_name = 'gc_requests'

urlpatterns = [
    # User dashboard
    path('dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
    
    # Request management
    path('create/', views.CreateRequestView.as_view(), name='create_request'),
    path('my-requests/', views.MyRequestsView.as_view(), name='my_requests'),
    path('request/<int:request_id>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('request/<int:request_id>/track/', views.TrackRequestView.as_view(), name='track_request'),
    
    # Labour views
    path('labour/dashboard/', views.LabourDashboardView.as_view(), name='labour_dashboard'),
    path('labour/requests/', views.LabourRequestsView.as_view(), name='labour_requests'),
    path('labour/request/<int:request_id>/', views.LabourRequestDetailView.as_view(), name='labour_request_detail'),
    path('labour/request/<int:request_id>/start/', views.StartWorkView.as_view(), name='start_work'),
    path('labour/request/<int:request_id>/complete/', views.CompleteWorkView.as_view(), name='complete_work'),
    
    # Councilor views
    path('councilor/dashboard/', views.CouncilorDashboardView.as_view(), name='councilor_dashboard'),
    path('councilor/requests/', views.CouncilorRequestsView.as_view(), name='councilor_requests'),
    path('councilor/assign/<int:request_id>/', views.AssignRequestView.as_view(), name='assign_request'),
    path('councilor/reports/', views.CouncilorReportsView.as_view(), name='councilor_reports'),
    path('councilor/report/<int:report_id>/approve/', views.ApproveReportView.as_view(), name='approve_report'),
    path('councilor/report/<int:report_id>/reject/', views.RejectReportView.as_view(), name='reject_report'),
    
    # Chairman views
    path('chairman/dashboard/', views.ChairmanDashboardView.as_view(), name='chairman_dashboard'),
    path('chairman/requests/', views.ChairmanRequestsView.as_view(), name='chairman_requests'),
    path('chairman/analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('chairman/overdue/', views.OverdueRequestsView.as_view(), name='overdue_requests'),
    
    # API endpoints (for mobile/AJAX)
    path('api/available-labour/', views.AvailableLabourAPIView.as_view(), name='available_labour_api'),
    path('api/ward-statistics/', views.WardStatisticsAPIView.as_view(), name='ward_statistics'),
    path('api/request/<int:request_id>/location/', views.RequestLocationAPIView.as_view(), name='request_location'),
    path('api/cancel-request/<int:request_id>/', views.CancelRequestAPIView.as_view(), name='cancel_request_api'),
]
