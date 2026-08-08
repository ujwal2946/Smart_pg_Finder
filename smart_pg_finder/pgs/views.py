from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PGForm
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Avg
from .models import PG, PGImage, Wishlist
import os
import uuid
import requests
import io
from PIL import Image
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
from decimal import Decimal, InvalidOperation

# -------- PG CRUD --------

@login_required(login_url='/dashboard/login/')
def add_pg(request, template_name='pgs/add_pg.html'):
    print("=== ADD PG DEBUG ===")
    if request.method == 'POST':
        print("POST data:", dict(request.POST))
        
        # Primary: Django Form (existing)
        form = PGForm(request.POST)
        print("Form valid:", form.is_valid())
        print("Form errors:", form.errors.as_data())
        
        if form.is_valid():
            print("Saving via FORM...")
            pg = form.save(commit=False)
            pg.owner = request.user
            pg.save()
            print("PG saved ID:", pg.id)

            messages.success(request, f'PG "{pg.name}" created! ID: {pg.id}')
            return redirect('/dashboard/owner/')
        
        # FALLBACK: Raw POST as per task spec
        print("FORM failed, trying RAW POST...")
        try:
            name = request.POST.get('name')
            location = request.POST.get('location')
            price = request.POST.get('price')
            
            if name and location and price:
                pg = PG.objects.create(
                    name=name.strip(),
                    location=location.strip(),
                    price=float(price),
                    owner=request.user,
                    description=request.POST.get('description', ''),
                    phone=request.POST.get('phone', ''),
                    owner_email=request.POST.get('owner_email', ''),
                    availability=request.POST.get('availability', 'available'),
                    is_wifi=request.POST.get('is_wifi') == 'on',
                    is_ac=request.POST.get('is_ac') == 'on',
                    is_food=request.POST.get('is_food') == 'on',
                )
                print("RAW PG saved ID:", pg.id)
                messages.success(request, f'PG "{name}" created via fallback!')
                return redirect('/dashboard/owner/')
        except Exception as e:
            print("RAW POST failed:", str(e))
        
        messages.error(request, f'Form errors: {form.errors}. Debug: {dict(request.POST)}')
    else:
        form = PGForm()
    
    return render(request, template_name, {'form': form, 'pg': None})

@login_required(login_url='/dashboard/login/')
def edit_pg(request, id):
    print("=== EDIT PG DEBUG ===", id)
    pg = get_object_or_404(PG, id=id, owner=request.user)
    
    if request.method == 'POST':
        print("POST data:", dict(request.POST))
        
        # Primary: Django Form
        form = PGForm(request.POST, instance=pg)
        print("Form valid:", form.is_valid())
        if form.is_valid():
            form.save()
            messages.success(request, f'PG "{pg.name}" updated!')
            return redirect('/dashboard/owner/')
        
        # FALLBACK: Direct update matching task spec
        print("FORM failed, trying direct update...")
        try:
            pg.name = request.POST.get('name', pg.name)
            pg.location = request.POST.get('location', pg.location)
            pg.price = float(request.POST.get('price', pg.price))
            pg.description = request.POST.get('description', pg.description)
            pg.phone = request.POST.get('phone', pg.phone)
            pg.owner_email = request.POST.get('owner_email', pg.owner_email)
            pg.availability = request.POST.get('availability', pg.availability)
            pg.is_wifi = request.POST.get('is_wifi') == 'on'
            pg.is_ac = request.POST.get('is_ac') == 'on'
            pg.is_food = request.POST.get('is_food') == 'on'
            pg.save()
            print("Direct update successful")
            messages.success(request, f'PG "{pg.name}" updated via fallback!')
            return redirect('/dashboard/owner/')
        except Exception as e:
            print("Direct update failed:", str(e))
        
        # Show errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
    else:
        form = PGForm(instance=pg)
    
    return render(request, 'pgs/add_pg.html', {'form': form, 'pg': pg})


@login_required(login_url='/dashboard/login/')
def delete_pg(request, id):
    pg = get_object_or_404(PG, id=id, owner=request.user)
    pg.delete()
    return redirect('/dashboard/owner/')


# -------- SEARCH --------

def search_page(request):
    return render(request, 'pgs/search_pgs.html')


def all_pgs_api(request):
    pgs = PG.objects.select_related('owner').prefetch_related('images').all().order_by('-is_featured', 'id')
    
    # Simple filtering logic (FIXED boolean handling)
    location = request.GET.get('location', '').strip()
    is_wifi = request.GET.get('is_wifi', 'false').lower() == 'true'
    is_ac = request.GET.get('is_ac', 'false').lower() == 'true'
    is_food = request.GET.get('is_food', 'false').lower() == 'true'
    
    print(f"DEBUG API: location='{location}', wifi={is_wifi}, ac={is_ac}, food={is_food}")  # TEMP DEBUG
    
    if location:
        pgs = pgs.filter(location__icontains=location)
    if is_wifi:
        pgs = pgs.filter(is_wifi=True)
    if is_ac:
        pgs = pgs.filter(is_ac=True)
    if is_food:
        pgs = pgs.filter(is_food=True)
    
    # Price filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    try:
        min_price = Decimal(min_price) if min_price else None
    except (InvalidOperation, TypeError):
        min_price = None
    try:
        max_price = Decimal(max_price) if max_price else None
    except (InvalidOperation, TypeError):
        max_price = None

    if min_price is not None and max_price is not None and min_price > max_price:
        min_price, max_price = max_price, min_price

    if min_price:
        pgs = pgs.filter(price__gte=min_price)
    if max_price:
        pgs = pgs.filter(price__lte=max_price)
    
    # Sorting
    sort = request.GET.get('sort')
    if sort == 'low_price':
        pgs = pgs.order_by('price')
    elif sort == 'high_price':
        pgs = pgs.order_by('-price')
    
    paginator = Paginator(pgs, 6)
    try:
        page = paginator.get_page(request.GET.get('page', 1))
    except:
        page = paginator.page(1)
    data = []
    for pg in page:
        img = pg.images.first()
        try:
            avg_rating = pg.review_set.aggregate(Avg('rating'))['rating__avg'] or 0.0
        except (AttributeError, KeyError):
            avg_rating = 0.0  # Safe default if no reviews model/relation
        data.append({
            'id': pg.id,
            'name': pg.name,
            'location': pg.location,
            'price': str(pg.price),
            'image_url': (img.image.url if img else '/static/images/default_pg.jpg') if img else '/static/images/default_pg.jpg',
            'is_wifi': pg.is_wifi,
            'is_ac': pg.is_ac,
            'is_food': pg.is_food,
            'avg_rating': round(float(avg_rating), 1),
            'is_available': pg.is_available,
            'is_featured': pg.is_featured,
            'owner_username': pg.owner.username,
        })

    return JsonResponse({
        'pgs': data,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'current_page': page.number,
        'total_pages': paginator.num_pages
    }, safe=False)


# -------- WISHLIST --------

def add_to_wishlist(request, id):
    pg = PG.objects.get(id=id)

    Wishlist.objects.get_or_create(
        user=request.user,
        pg=pg
    )

    return redirect('/pg/search/')


def wishlist_page(request):
    items = Wishlist.objects.filter(user=request.user)

    return render(request, 'pgs/wishlist.html', {
        'items': items
    })


def remove_from_wishlist(request, id):
    Wishlist.objects.filter(id=id, user=request.user).delete()
    return redirect('/pg/wishlist/')

@login_required(login_url='/dashboard/login/')
def toggle_availability(request, pg_id):
    if request.method == 'POST':
        pg = get_object_or_404(PG, id=pg_id, owner=request.user)
        pg.is_available = not pg.is_available
        pg.availability = 'available' if pg.is_available else 'booked'
        pg.save()
        return JsonResponse({
            'success': True,
            'is_available': pg.is_available,
            'status_text': 'Available' if pg.is_available else 'Full',
            'badge_class': 'bg-success' if pg.is_available else 'bg-danger'
        })
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required(login_url='/dashboard/login/')
@require_http_methods(["POST"])
def ajax_update_pg(request, pg_id):
    try:
        pg = get_object_or_404(PG, id=pg_id, owner=request.user)
        
        # Get updates from JSON body
        body = json.loads(request.body)
        updates = body.get('updates', {})
        
        # Allowed updatable fields (secure)
        allowed_fields = {'price', 'location', 'name', 'phone', 'owner_email', 'is_wifi', 'is_ac', 'is_food'}
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(pg, field, value)
        
        pg.save()
        
        return JsonResponse({
            'success': True,
            'message': 'PG updated successfully',
            'updated': {k: str(v) for k, v in updates.items()}
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def pg_detail(request, id):
    pg = PG.objects.only('id', 'name', 'location', 'price', 'description', 'is_wifi', 'is_ac', 'is_food', 'availability', 'owner', 'is_available', 'phone', 'owner_email').prefetch_related('images').get(id=id)
    images = pg.images.all()
    reviews = pg.review_set.all()
    avg_rating = pg.review_set.aggregate(Avg('rating'))['rating__avg'] or 0

    return render(request, 'pgs/pg_detail.html', {
        'pg': pg,
        'images': images,
        'reviews': reviews,
        'avg_rating': round(float(avg_rating), 1),
    })

@login_required(login_url='/dashboard/login/')
def toggle_pg(request, id):
    pg = get_object_or_404(PG, id=id, owner=request.user)
    pg.is_available = not pg.is_available
    pg.availability = 'available' if pg.is_available else 'booked'
    pg.save()
    return redirect('/dashboard/owner/')

