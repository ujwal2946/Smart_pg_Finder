from django.urls import path
from . import views

urlpatterns = [
    # PG CRUD
    path('add/', views.add_pg, name='add_pg'),
    path('simple/', views.add_pg, {'template_name': 'simple_add_pg.html'}, name='simple_add_pg'),
    path('edit/<int:id>/', views.edit_pg, name='edit_pg'),
    path('delete/<int:id>/', views.delete_pg, name='delete_pg'),
    path('toggle-availability/<int:pg_id>/', views.toggle_availability, name='toggle_availability'),
    path('toggle/<int:id>/', views.toggle_pg, name='toggle_pg'),
    path('ajax-update/<int:pg_id>/', views.ajax_update_pg, name='ajax_update_pg'),

    # Search system
    path('search/', views.search_page, name='search_page'),
    path('api/', views.all_pgs_api, name='pg_api'),

    # Wishlist
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('wishlist/add/<int:id>/', views.add_to_wishlist, name='add_wishlist'),
    path('wishlist/remove/<int:id>/', views.remove_from_wishlist, name='remove_wishlist'),
    path('<int:id>/', views.pg_detail, name='pg_detail'),
]
