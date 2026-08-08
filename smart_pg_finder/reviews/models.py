from django.db import models
from users.models import User
from pgs.models import PG

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pg = models.ForeignKey(PG, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.pg.name} ({self.rating})"