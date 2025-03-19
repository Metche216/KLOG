""" Test Cases for the App Models """

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now as tzn
from core.models import Tournament, TEvent, Player

def create_user(email, password):
    """ Create and return a new user """
    return get_user_model().objects.create_user(email=email, password=password)

def create_tevent(user, **params ):
    """ Create and return a tournament event instance """
    tournament = Tournament.objects.create(name='Ranking')
    defaults = {
        'name': 'Padel Las Palmas',
        'sport': 'Padel',
        'start_date': '2025-05-17',
        'end_date': '2025-10-25',
        'status': 'open',
        'tournament': tournament,
    }

    defaults.update(params)
    tevent = TEvent.objects.create(created_by=user, **defaults)
    return tevent

class ModelsTests(TestCase):
    """ Test suite for the app models """

    def setUp(self):
        self.user = create_user('test@example.com', 'pass123')

    def test_create_new_tevent(self):
        """ Test creation of a tournament event """
        t = Tournament.objects.create(name='Ranking')
        tevent = TEvent.objects.create(
            created_by=self.user,
            name='PadelFinde',
            sport='Padel',
            start_date=tzn(),
            end_date=tzn(),
            tournament=t,
            )

        self.assertEqual(tevent.created_by, self.user)
        self.assertEqual(tevent.tournament.name, 'Ranking')

    def test_create_new_player(self):
        """ Test creating a player for a Match """
        t = Tournament.objects.create(name='Escalerilla')
        Player.objects.create(user=self.user, tournament=t)

        players = Player.objects.all()

        self.assertEqual(players.count(),1)
        self.assertTrue(Player.objects.filter(user=self.user).exists())