from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class PG(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    is_wifi = models.BooleanField(default=False)
    is_ac = models.BooleanField(default=False)
    is_food = models.BooleanField(default=False)

    availability = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    phone = models.CharField(max_length=15, blank=True)
    owner_email = models.EmailField(blank=True)
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        previous = None
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).only('availability', 'is_available').first()

        if previous:
            availability_changed = self.availability != previous.availability
            is_available_changed = self.is_available != previous.is_available

            if availability_changed and not is_available_changed:
                self.is_available = self.availability == 'available'
            else:
                self.availability = 'available' if self.is_available else 'booked'
        else:
            self.is_available = self.availability == 'available' if self.availability else self.is_available
            self.availability = 'available' if self.is_available else 'booked'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PGImage(models.Model):
    pg = models.ForeignKey(PG, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='pg_images/')


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pg = models.ForeignKey(PG, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.pg.name}"

