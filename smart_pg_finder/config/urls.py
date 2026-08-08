from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from users.views import forgot_password_view

def home(request):
    if request.user.is_authenticated:
        if request.user.role == 'user':
            return redirect('/dashboard/user/')
        elif request.user.role == 'owner':
            return redirect('/dashboard/owner/')
        else:
            return redirect('/dashboard/admin/')
    return redirect('/dashboard/login/')

def logout_view(request):
    logout(request)
    return redirect('/dashboard/login/')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('users.urls')),
    path('pg/', include('pgs.urls')),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('review/', include('reviews.urls')),
    path('request/', include('requests_app.urls')),
]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)