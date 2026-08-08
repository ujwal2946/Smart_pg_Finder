from django.urls import path
from .views import (
    send_request,
    owner_requests,
    approve_request,
    reject_request,
    user_requests
)

urlpatterns = [
    path('add/<int:id>/', send_request),
    path('owner/', owner_requests),
    path('approve/<int:id>/', approve_request),
    path('reject/<int:id>/', reject_request),
    path('user/', user_requests),
]