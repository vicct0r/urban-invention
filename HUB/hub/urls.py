from django.urls import path
from .views import CdRegisterAPIView, CdPatchAPIView, CdRequestAPIView, CdListAPIView


urlpatterns = [
    path('cd/register/', CdRegisterAPIView.as_view(), name='cd_register'),
    path('cd/update/<slug:slug>/', CdPatchAPIView.as_view(), name='cd_edit'),
    path('cd/request/', CdRequestAPIView.as_view(), name='cd_request'),
    path('cd/info/', CdListAPIView.as_view(), name='cd_info'),    
    path('cd/info/slug/<slug:slug>/', CdListAPIView.as_view(), name='cd_detail_slug'),
    path('cd/info/id/<int:pk>/', CdListAPIView.as_view(), name='cd_detail_id'),
]