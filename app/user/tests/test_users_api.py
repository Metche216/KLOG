"""
Tests for the users API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import BasePlayer

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')

def create_new_user(**params):
    """ Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUsersAPITests(TestCase):
    """ Tests public features of the users API """

    def setUp(self):
        self.client = APIClient()

    def test_create_new_user(self):
        """ Create a new user successfully """
        user = create_new_user(email='test@example.com', password='123qwerty')
        self.assertIn(user, get_user_model().objects.all())

    def test_create_new_user_api(self):
        """ Create a new user through api """
        payload = {
            'email': 'test@example.com',
            'password': '123qwerty',
            'name': 'User Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['email'], payload['email'])
        user = get_user_model().objects.get(email=payload['email']) #gets the user from db
        self.assertTrue(user.check_password(payload['password']))   #checks if the users pasword matches the payload encrypted password
        self.assertNotIn('password', res.data)                      #checks that the password is not returned.

    def test_creating_new_user_creates_users_player(self):
        """ Tests player creation upon user creation """
        payload = {
            'email': 'test@example.com',
            'password': '123qwerty',
            'name': 'User Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        user = get_user_model().objects.get(email=payload['email'])
        player = BasePlayer.objects.get(user=user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(player.name, payload['name'])


    def test_user_with_email_exists(self):
        """ Test if a user email already exists """
        get_user_model().objects.create_user(email='test@example.com', password='pass123')
        payload = {
            'email': 'test@example.com',
            'password': '123qwerty',
            'name': 'User Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """ Test creating a new token successfully"""
        user_data = {
            'email': 'test@example.com',
            'password': '123qwerty',
            'name': 'User Name'
        }

        create_new_user(**user_data)
        payload = {
            'email': user_data['email'],
            'password': user_data['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """ Tests tokens is created only for registered users """
        user = create_new_user(email='test@example.com', password='abc123')
        payload = {
            'email': 'test@example.com',
            'password': 'different123'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns error"""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dennial_for_unauthorized_users(self):
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUsersAPITests(TestCase):
    """ Tests for functionality on authenticated users """

    def setUp(self):
        self.user = create_new_user(email='test@example.com', password='abc123', name='Test User')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_allow_retrieve_profile(self):
        """ Test retrieving profile from logged user """
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_profile_info(self):
        """ Tests updating user profile is successfull"""
        payload = {
            'name': 'Another name',
            'password':'new_password'
        }

        res = self.client.patch(PROFILE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], payload['name'])