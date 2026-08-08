from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import RegisterForm


# DASHBOARDS
from pgs.models import PG, Wishlist
from requests_app.models import PGRequest
from users.models import User as CustomUser

@login_required(login_url='/dashboard/login/')
def user_dashboard(request):
    recommended = PG.objects.only('id', 'name', 'location', 'price', 'is_wifi', 'is_ac', 'is_food').prefetch_related('images').all()[:3]
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    active_requests = PGRequest.objects.filter(user=request.user, status='pending').count()
    
    return render(request, 'users/user_dashboard.html', {
        'recommended': recommended,
        'wishlist_count': wishlist_count,
        'active_requests': active_requests
    })

@login_required(login_url='/dashboard/login/')
def owner_dashboard(request):
    my_pgs = PG.objects.filter(owner=request.user).select_related('owner').prefetch_related('images')
    for pg in my_pgs:
        pg.request_count = PGRequest.objects.filter(pg=pg).count()

    requests_received = PGRequest.objects.filter(pg__owner=request.user, status='pending').count()
    total_pgs = PG.objects.filter(owner=request.user).count()
    total_requests = PGRequest.objects.filter(pg__owner=request.user).count()
    approved = PGRequest.objects.filter(pg__owner=request.user, status='approved').count()

    return render(request, 'users/owner_dashboard.html', {
        'pgs': my_pgs,
        'total_pgs': total_pgs,
        'total_requests': total_requests,
        'approved': approved,
        'pg_count': my_pgs.count(),
        'requests_received': requests_received
    })

@login_required(login_url='/dashboard/login/')
def admin_dashboard(request):
    stats = {
        'total_users': CustomUser.objects.count(),
        'total_pgs': PG.objects.count(),
        'total_requests': PGRequest.objects.count()
    }
    return render(request, 'users/admin_dashboard.html', {'stats': stats})


@login_required(login_url='/dashboard/login/')
def profile_view(request):
    return render(request, 'users/profile.html', {
        'user': request.user
    })


# LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            # redirect based on role
            if user.role == 'user':
                return redirect('/dashboard/user/')
            elif user.role == 'owner':
                return redirect('/dashboard/owner/')
            else:
                return redirect('/dashboard/admin/')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'users/login.html')

# REGISTER
def register_view(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registered Successfully! Please login.")
            return redirect('/dashboard/login/')
        else:
            messages.error(request, "Registration failed. Please check the form.")

    return render(request, 'users/register.html', {'form': form})


def forgot_password_view(request):
    # Step 1: Identify User
    # Step 2: Reset Password
    step = request.session.get('reset_step', 1)
    reset_username = request.session.get('reset_username')

    if request.method == 'POST':
        if 'identify' in request.POST:
            username = request.POST.get('username')
            if CustomUser.objects.filter(username=username).exists():
                request.session['reset_step'] = 2
                request.session['reset_username'] = username
                messages.success(request, f"User '{username}' identified. Please enter a new password.")
                return redirect('/forgot-password/')
            else:
                messages.error(request, "Username not found in our ecosystem.")
        
        elif 'reset' in request.POST:
            new_pass = request.POST.get('password1')
            confirm_pass = request.POST.get('password2')
            
            if new_pass != confirm_pass:
                messages.error(request, "Passwords do not match.")
            elif len(new_pass) < 8:
                messages.error(request, "New password must be at least 8 characters.")
            else:
                user = CustomUser.objects.get(username=reset_username)
                user.set_password(new_pass)
                user.save()
                
                # Cleanup session
                del request.session['reset_step']
                del request.session['reset_username']
                
                messages.success(request, "Password updated successfully. Please login.")
                return redirect('/dashboard/login/')

    return render(request, 'users/forgot_password.html', {
        'step': step,
        'reset_username': reset_username
    })

