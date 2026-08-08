from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PGRequest
from pgs.models import PG


# -------- SEND REQUEST --------

@login_required(login_url='/dashboard/login/')
def send_request(request, id):
    pg = PG.objects.get(id=id)

    PGRequest.objects.get_or_create(
        user=request.user,
        pg=pg
    )

    return redirect('/pg/search/')


# -------- OWNER VIEW --------

@login_required(login_url='/dashboard/login/')
def owner_requests(request):
    requests = PGRequest.objects.filter(pg__owner=request.user)

    return render(request, 'requests/owner_requests.html', {
        'requests': requests
    })


# -------- APPROVE / REJECT --------

@login_required(login_url='/dashboard/login/')
def approve_request(request, id):
    req = PGRequest.objects.get(id=id)
    req.status = 'approved'
    req.save()
    
    pg = req.pg
    pg.is_available = False
    pg.save()
    
    return redirect('/request/owner/')


@login_required(login_url='/dashboard/login/')
def reject_request(request, id):
    req = PGRequest.objects.get(id=id)
    req.status = 'rejected'
    req.save()
    return redirect('/request/owner/')


# -------- USER VIEW --------

@login_required(login_url='/dashboard/login/')
def user_requests(request):
    requests = PGRequest.objects.filter(user=request.user).select_related('pg').only('pg__id', 'pg__name', 'pg__location').prefetch_related('pg__images')

    return render(request, 'requests/user_requests.html', {
        'requests': requests
    })
