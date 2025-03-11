""" DB Models """

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
class UserManager(BaseUserManager):
    """ Manager for the User Model """
    def create_user(self, email, password=None, **extra_fields):
        """ Create and return a new user """
        if not email:
            raise ValueError(_('User must have an email address.'))
        
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """ User Model """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'


class Tournament(models.Model):
    """ A model to represent tournament's structure """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class TEvent(models.Model):
    """ A model for tournament instances """
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='tevent')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    sport = models.CharField(max_length=255)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.CharField(max_length=20, choices=[
        ("open", "Open"),
        ("in_progress", "In progress"),
        ("completed", "Completed")
    ], default= "open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - ({self.tournament.name})'

