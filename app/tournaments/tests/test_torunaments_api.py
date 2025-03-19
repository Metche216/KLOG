from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from tournaments.serializers import TournamentSerializer, TEventSerializer
from core.models import Tournament, TEvent


TOURNAMENT_URL = reverse('tournament:tournament-list')
TEVENT_URL = reverse('tournament:tevent-list')

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
        tournament1 = Tournament.objects.create(name='Padel')
        tournament2 = Tournament.objects.create(name='Tennis')

        res = self.client.get(TOURNAMENT_URL)
        tournaments = Tournament.objects.all()
        serializer = TournamentSerializer(tournaments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_new_tournament_fails_for_regular_users(self):
        """ Test create tournament for non-Admins fails """
        payload = {
            'name': 'Ranking',
            'description': 'A ranking method for sports tournaments'
        }
        res = self.client.post(TOURNAMENT_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_new_tevent(self):
        """ Test creation of a tournament event """
        tevent = create_tevent(user=self.user)
        self.assertEqual(tevent.created_by, self.user)
        self.assertEqual(tevent.tournament.name, 'Ranking')

    def test_create_new_tevent_API(self):
        """ Test creating a new tournament EVENT through API """
        t = Tournament.objects.create(name='Super Copa')

        payload = {
            'tournament':f'{t.id}',
            'sport': 'Football',
            'name': 'TorneoCorto',
            'start_date': '2025-05-17',
            'end_date': '2025-06-17'
        }

        res = self.client.post(TEVENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tevent = TEvent.objects.get(id=res.data['id'])
        for k,v in payload.items():
            if k != 'tournament':
                if 'date' in k:
                    fecha = getattr(tevent, k).strftime('%Y-%m-%d')
    def test_create_new_tevent_API(self):
        """ Test creating a new tournament EVENT through API """
        t = Tournament.objects.create(name='Super Copa')

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
        t = Tournament.objects.create(name='Super Copa')

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
        t = Tournament.objects.create(name='Super Copa')

        payload = {
            'tournament':f'{t.id}',
            'sport': 'Football',
            'name': 'TorneoSemana',
            'start_date': '2025-05-17',
            'end_date': '2025-05-05'
        }

        res = self.client.post(TEVENT_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


