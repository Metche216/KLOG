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
    players = models.ManyToManyField('BasePlayer', blank=True)
    teams_n = models.IntegerField()

    def __str__(self):
        return self.name


class TEvent(models.Model):
    """ A model for tournament instances """
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='tevent')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    sport = models.CharField(max_length=255)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=False, null=False)
    players = models.ManyToManyField('TournamentPlayer')
    status = models.CharField(max_length=20, choices=[
        ("open", "Open"),
        ("in_progress", "In progress"),
        ("completed", "Completed")
    ], default= "open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - ({self.tournament.name})'

    def advance(self):
        """ Move one step forward in tevent status """
        if self.status == 'open':
            self.status = 'in_progress'
        elif self.status == 'in_progress':
            self.status = 'completed'
        else:
            pass

        self.save()

class BasePlayer(models.Model):
    """ A model for a tournament general player """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='baseplayer')
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.user.name


class TournamentPlayer(models.Model):
    """ A generic model for the tournament players """
    player = models.ForeignKey('BasePlayer', on_delete=models.CASCADE, related_name='tplayer')
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'tournament')

    def __str__(self):
        return f'{self.player.user.name}'


class Team(models.Model):
    """ Model representation for the teams """
    name = models.CharField(max_length=100)
    players = models.ManyToManyField('TournamentPlayer', related_name='teams')
    tevent = models.ForeignKey(TEvent, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name