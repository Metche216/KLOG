"""
Tests for the users API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

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
        