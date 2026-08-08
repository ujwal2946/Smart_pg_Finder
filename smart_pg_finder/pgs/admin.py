from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import PG, PGImage, Wishlist


class PGAdmin(admin.ModelAdmin):
    list_display = ('name', 'edit_pg', 'delete_pg')

    def edit_pg(self, obj):
        url = reverse('admin:pgs_pg_change', args=[obj.id])
        return format_html('<a href="{}">Edit</a>', url)

    def delete_pg(self, obj):
        url = reverse('admin:pgs_pg_delete', args=[obj.id])
        return format_html('<a href="{}">Delete</a>', url)


admin.site.register(PG, PGAdmin)
admin.site.register(PGImage)
admin.site.register(Wishlist)