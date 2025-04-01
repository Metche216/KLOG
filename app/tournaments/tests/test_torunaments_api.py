from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from tournaments.serializers import TournamentSerializer, TEventSerializer
from core.models import Tournament, TEvent, BasePlayer, TournamentPlayer


TOURNAMENT_URL = reverse('tournament:tournament-list')
TEVENT_URL = reverse('tournament:tevent-list')
def tdetail_url(t_id):
    """ Return the detailed url for a specific tournament """
    return reverse('tournament:tournament-detail', args=[t_id])

def detail_url(tevent_id):
    """ Return the detailed url for a specific tevent """
    return reverse('tournament:tevent-detail', args=[tevent_id])

def create_user(email, password, **kwargs):
    """ Create and return a new user """
    return get_user_model().objects.create_user(email=email, password=password, **kwargs)

def create_tournament(name, **params):
    tournament = Tournament.objects.create(name=name, **params)
    return tournament

def create_tevent(user, **params ):
    """ Create and return a tournament event instance """
    tournament = create_tournament(name='Ranking', teams_n=2)
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

def add_new_player_to_tournament(tournament, base_player):
            """
            Automatically creates a new player for a specific tournament
            *Arguments*
            tournament= from Tournament Model,
            base_player= from BasePlayer Model

            """
            tournament.players.add(base_player)



class PublicTournamentAPITests(TestCase):
    """ Tests tournaments API for unauthenticated users """

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_tournaments_unauthorized(self):
        """ Tests tournaments are available only for authenticated users """
        res = self.client.get(TOURNAMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTournamentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='Test@example.com', name='Test User', password='abc123pass')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tournaments_successfull(self):
        """ Test list of tournaments for authenticated users """
        tournament1 = create_tournament(name='Padel', teams_n=2)
        tournament2 = create_tournament(name='Tennis', teams_n=2)

        res = self.client.get(TOURNAMENT_URL)
        tournaments = Tournament.objects.all()
        serializer = TournamentSerializer(tournaments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_new_tournament_with_players(self):
        """ Test create tournament for non-Admins fails """
        bp1 = self.user.baseplayer
        payload = {
            'name': 'Ranking',
            'description': 'A ranking method for sports tournaments',
            'players':[bp1.id],
            'teams_n':2
        }
        res = self.client.post(TOURNAMENT_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tournament = Tournament.objects.first()
        self.assertEqual(tournament.name, payload['name'])
        self.assertEqual(tournament.players.count(), 1)

    def test_create_new_tevent(self):
        """ Test creation of a tournament event """
        tevent = create_tevent(user=self.user)
        self.assertEqual(tevent.created_by, self.user)
        self.assertEqual(tevent.tournament.name, 'Ranking')

    def test_create_new_tevent_API(self):
        """ Test creating a new tournament EVENT through API """
        t = create_tournament(name='Super Copa', teams_n=2)

        payload = {
            'tournament':f'{t.id}',
            'sport': 'Football',
            'name': 'TorneoCorto',
            'start_date': '2025-05-17',
            'end_date': '2025-06-17'
        }

        res = self.client.post(TEVENT_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tevent = TEvent.objects.get(id=res.data['id'])
        for k,v in payload.items():
            if k != 'tournament':
                if 'start' in k:
                    fecha = getattr(tevent, k).strftime('%Y-%m-%d')
                    self.assertEqual(fecha, '2025-05-17')
                elif 'end' in k:
                    pass
                else:
                    self.assertEqual(getattr(tevent,k),v)

    def test_create_new_tevent_without_end_date_fails(self):
        """" Test creating open tevents without end_date fails """
        t = create_tournament(name='Super Copa', teams_n=2)

        payload = {
            'tournament':f'{t.id}',
            'sport': 'Football',
            'name': 'TorneoSemana',
            'start_date': '2025-05-17',
            'end_date': ''
        }

        res = self.client.post(TEVENT_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_date_is_sooner_than_start_date(self):
        """ Test dates in a tevent are according """
        t = create_tournament(name='Super Copa', teams_n=2)
        payload = {
            'tournament':f'{t.id}',
            'sport': 'Football',
            'name': 'TorneoSemana',
            'start_date': '2025-05-17',
            'end_date': '2025-05-05'
        }

        res = self.client.post(TEVENT_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creating_new_tournament_player(self):
        """ Test the creation of tournament players """
        t = create_tevent(user=self.user)
        tournament = t.tournament
        tournament.players.add(self.user.baseplayer)
        tplayer = TournamentPlayer.objects.create(player=self.user.baseplayer, tournament=tournament)
        t.players.add(tplayer)

        self.assertIn(self.user.baseplayer, tournament.players.all())
        self.assertEqual(t.players.count(), 1)

    def test_player_assambly_for_tevent(self):
        """ Test retrieving selected players for the tevnet"""
        tevent = create_tevent(user=self.user)
        user2 = create_user(email='test2@example.com', name='Rolandito', password='abc123pass')
        bp2 = user2.baseplayer
        bp1 = self.user.baseplayer
        t = Tournament.objects.first()
        player_list = [bp1, bp2]
        for player in player_list:
            add_new_player_to_tournament(t, player)

        self.assertIn(bp2, t.players.all())
        self.assertIn(bp1, t.players.all())

        payload = {
            'tournament': t.id,
            'players': [bp1.id, bp2.id]
        }

        url = detail_url(tevent.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tevent.refresh_from_db()
        self.assertEqual(tevent.tournament.name, t.name)
        self.assertEqual(tevent.players.count(), 2)

    def test_remove_players_from_a_tevent(self):
        """ Test removing players from the tevent """
        user2 = create_user(email='test2@example.com', name='Rolandito', password='abc123pass')
        user3 = create_user(email='test3@example.com', name='Fabiancito', password='abc123pass')
        tevent = create_tevent(user=self.user)
        t = tevent.tournament
        bp1 = self.user.baseplayer
        bp2 = user2.baseplayer
        bp3 = user3.baseplayer
        t.players.add(bp1)
        t.players.add(bp2)
        t.players.add(bp3)
        tplayer = TournamentPlayer.objects.create(player=bp1, tournament=t)
        tplayer2 = TournamentPlayer.objects.create(player=bp2, tournament=t)
        tplayer3 = TournamentPlayer.objects.create(player=bp3, tournament=t)
        tplayer_list = [tplayer, tplayer2, tplayer3]
        for player in tplayer_list:
            tevent.players.add(player)
        self.assertEqual(t.players.all().count() ,3 )
        self.assertEqual(tevent.players.all().count(), 3)

        payload = {
            'tournament': t.id,
            'players': [bp1.id, bp2.id]
        }

        url = detail_url(tevent.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, 200)
        tevent.refresh_from_db()
        self.assertEqual(tevent.players.all().count(), 2)

    def test_create_tournament_player_on_tournament_update(self):
        """ Test the creation of tournament players when baseplayer is added to tournament """

        user2 = create_user(email='user2@example.com', name='Matias', password='usaerpass123')
        t = create_tournament(name='Escalerilla', teams_n=2)
        bp1 = self.user.baseplayer
        bp2 = user2.baseplayer
        payload = {
            'players':[bp1.id, bp2.id]
        }
        url = tdetail_url(t.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(t.players.all().count(), 2)
        all_Tplayers = TournamentPlayer.objects.all()
        self.assertEqual(all_Tplayers.count(), 2)


class PrivateMainTournamentAPITests(TestCase):
    """ Test the functionality for tevents in a especific tournament """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user('user@example.com', 'textpass123', name='user1 name')
        self.userbp = self.user.baseplayer
        self.user2 = create_user('user2@example.com', 'textpass123', name='user2 name')
        self.user2bp = self.user2.baseplayer
        tournament_data = {'players':[self.userbp.id, self.user2bp.id]}
        self.t = create_tournament(name='Main Tournament', teams_n=2)
        for player in tournament_data['players']:
            TournamentPlayer.objects.create(tournament=self.t, player=BasePlayer.objects.get(id=player))
            self.t.players.add(player)
        self.client.force_authenticate(self.user)

    def test_retrieving_players_from_tevent(self):
        """ test that all TPlayers are retrieved from a tevent"""

        tevent = TEvent.objects.create(
            tournament=self.t,
            created_by=self.user,
            name='Sabado 10',
            sport='Padel',
            start_date='2025-05-17',
            end_date='2025-10-20',
            )

        self.assertIn(tevent, TEvent.objects.all())

        #Get a tevent detail and add all the Tournament Players created for the tournament

        url = detail_url(tevent.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

