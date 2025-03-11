from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from tournaments.serializers import TournamentSerializer
from core.models import Tournament, TEvent


TOURNAMENT_URL = reverse('tournament:tournament-list')
TEVENT_URL = reverse('tevent:create')

def create_tevent(user, **params ):
    """ Create and return a tournament event instance """
    tournament = Tournament.objects.create(name='Ranking')
    defaults = {
        'name': 'Padel Las Palmas',
        'sport': 'Padel',
        'start_date': '17-05-2025',
        'end_date': '25-10-2025',
        'status': 'open',
        'tournament': tournament,
    }

    defaults.update(params)
    tevent = TEvent.objects.create(user=user, **defaults)
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
        """ Test creation of a tournament instance for authorized users """
        create_tevent(user=self.user)
        res = self.client.post()
    