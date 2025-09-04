from django.urls import path
from .views import CdRegisterAPIView, CdPatchAPIView, CdRequestAPIView


urlpatterns = [
    path('cd/register/', CdRegisterAPIView.as_view(), name='cd_register'),
    path('cd/update/<slug:slug>/', CdPatchAPIView.as_view(), name='cd_edit'),
    path('cd/request/<str:product>/<int:quantity>/', CdRequestAPIView.as_view(), name='cd_request')
]