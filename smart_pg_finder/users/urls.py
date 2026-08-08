from django.urls import path
from .views import user_dashboard, owner_dashboard, admin_dashboard, login_view, register_view, profile_view

urlpatterns = [
    path('login/', login_view),
    path('register/', register_view),
    path('profile/', profile_view),

    path('user/', user_dashboard),
    path('owner/', owner_dashboard),
    path('admin/', admin_dashboard),
]