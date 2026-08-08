from django.apps import AppConfig
from django.db import connection

class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        # Clear all sessions on startup
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_session")
