from django.urls import path
from .views import add_review

urlpatterns = [
    path('add/<int:id>/', add_review),
]