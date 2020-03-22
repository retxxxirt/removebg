import os
from unittest import TestCase

from requests import HTTPError

from removebg import requests
from removebg.exceptions import APIError


class RequestsTestCase(TestCase):
    def test_make_url(self):
        self.assertEqual(requests.make_url('profile'), 'https://www.remove.bg/profile')

    def test_make_api_url(self):
        self.assertEqual(requests.make_api_url('removebg'), 'https://api.remove.bg/v1.0/removebg')

    def test_make_request(self):
        self.assertEqual(requests.make_request('GET', 'https://www.remove.bg/').status_code, 200)
        self.assertRaises(HTTPError, requests.make_request, 'GET', 'https://www.remove.bg/404')

    def test_make_uri_request(self):
        self.assertEqual(requests.make_uri_request('GET', 'profile').status_code, 200)
        self.assertRaises(HTTPError, requests.make_uri_request, 'GET', '404')

    def test_make_api_request(self):
        self.assertEqual(requests.make_api_request(
            'POST', 'removebg', os.environ.get('REMOVEBG_TOKEN'),
            data={'image_url': 'https://via.placeholder.com/625x400'}
        ).status_code, 200)

        self.assertRaises(APIError, requests.make_api_request, 'POST', 'removebg', '')
