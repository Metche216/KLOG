""" Test Cases for the App Models """

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now as tzn
from django.db.utils import IntegrityError
from core.utils import create_tournament_tevent_and_team
from core.models import (
    Tournament,
    TEvent,
    BasePlayer,
    TournamentPlayer,
    Team
    )


def create_user(email, password,**kwargs):
    """ Create and return a new user """
    return get_user_model().objects.create_user(email=email, password=password, **kwargs)

def create_tevent(user, t=None, **params ):
    """ Create and return a tournament event instance """
    if not t:
        t = Tournament.objects.create(name='Ranking', teams_n=2)

    defaults = {
        'name': 'Padel Las Palmas',
        'sport': 'Padel',
        'start_date': '2025-05-17',
        'end_date': '2025-10-25',
        'status': 'open',
        'tournament': t,
    }

    defaults.update(params)
    tevent = TEvent.objects.create(created_by=user, **defaults)
    return tevent

class ModelsTests(TestCase):
    """ Test suite for the app models """

    def setUp(self):
        self.user = create_user('test@example.com', 'pass123')


    def test_base_player_automatic_creation(self):
        """ Test the creation of a base player when a user is created """
        self.assertTrue(self.user.baseplayer)

    def test_create_new_tevent(self):
        """ Test creation of a tournament event """
        t = Tournament.objects.create(name='Ranking', teams_n=2)
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
        t = Tournament.objects.create(name='Escalerilla', teams_n=2)

        players = BasePlayer.objects.all()

        self.assertEqual(players.count(),1)
        self.assertTrue(BasePlayer.objects.filter(user=self.user).exists())

    def test_error_when_duplicating_base_players(self):
        """ Tests creating two players for the same user fails """
        t = Tournament.objects.create(name='Escalerilla', teams_n=2)
        player1 = self.user.baseplayer
        self.assertIn(player1, BasePlayer.objects.all())

        with self.assertRaises(IntegrityError):
            BasePlayer.objects.create(user=self.user)

    def test_create_tournament_specific_player(self):
        """ Tests creating a player for a specific tournament """
        t = Tournament.objects.create(name='Escalerilla', teams_n=2)
        self.user.name = 'Marcelo'
        player = self.user.baseplayer
        padel_player = TournamentPlayer.objects.create(tournament=t, player=player)

        all_tour_players = TournamentPlayer.objects.all()
        self.assertEqual(all_tour_players.count(), 1)
        self.assertEqual(self.user.name, player.name)
        self.assertEqual(self.user.name, padel_player.player.name)



    def test_create_new_team_and_assign_players(self):
        """ Test creating a new team and assigning players to it """
        new_team = create_tournament_tevent_and_team(self.user)
        teams = Team.objects.all()
        self.assertEqual(new_team.players.count(), 2)
        self.assertEqual(teams.count(), 1)
        self.assertEqual(teams.first().players.count(),2)






