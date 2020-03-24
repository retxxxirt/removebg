import os
import warnings
from base64 import b64encode
from unittest import TestCase
from uuid import uuid4

import requests
from tempmail import Tempmail

from removebg import exceptions
from removebg.removebg import RemoveBg


class RemoveBgTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        warnings.simplefilter('ignore', ResourceWarning)
        super().setUpClass()

    def setUp(self):
        self.client = RemoveBg(
            os.environ.get('API_TOKEN'),
            os.environ.get('SESSION_TOKEN'),
            os.environ.get('ANTICAPTCHA_TOKEN')
        )

        super().setUp()

    def test_token_required(self):
        self.assertRaises(exceptions.TokenRequired, RemoveBg().create_account)
        self.assertRaises(exceptions.TokenRequired, RemoveBg().get_available_credits)
        self.assertRaises(exceptions.TokenRequired, RemoveBg().remove_background)

    def test_remove_background(self):
        self.client.remove_background(image_url='https://via.placeholder.com/625x400')

    def test_remove_background_from_file(self):
        with open(filename := f'{uuid4()}.png', 'wb') as file:
            file.write(requests.get('https://via.placeholder.com/625x400').content)

        self.client.remove_background_from_file(filename)
        os.remove(filename)

    def test_remove_background_from_url(self):
        self.client.remove_background_from_url('https://via.placeholder.com/625x400')

    def test_remove_background_from_base64(self):
        with open(filename := f'{uuid4()}.png', 'wb') as file:
            file.write(requests.get('https://via.placeholder.com/625x400').content)

        with open(filename, 'rb') as file:
            self.client.remove_background_from_base64(b64encode(file.read()))

        os.remove(filename)

    def test_create_account(self):
        self.client.create_account(Tempmail().email, 'Pa$$w0rd')

        self.assertRaises(
            exceptions.AccountCreationFailed, self.client.create_account,
            os.environ.get('REMOVEBG_USERNAME'), 'Strong-Pa$$w0rd'
        )

    def test_login_using_credentials(self):
        client = RemoveBg(anticaptcha_token=os.environ.get('ANTICAPTCHA_TOKEN'))
        client.login(os.environ.get('REMOVEBG_USERNAME'), os.environ.get('REMOVEBG_PASSWORD'))

        self.assertIsInstance(client.session_token, str)
        self.assertIsInstance(client.api_token, str)

        self.assertRaises(
            exceptions.LoginFailed, client.login,
            os.environ.get('REMOVEBG_USERNAME'), 'invalid-password'
        )

    def test_login_using_session_token(self):
        (client := RemoveBg()).login(session_token=os.environ.get('SESSION_TOKEN'))
        self.assertIsInstance(client.api_token, str)

    def test_get_available_credits(self):
        self.assertIsInstance(self.client.get_available_credits(), float)

    def test_get_available_previews(self):
        self.assertIsInstance(self.client.get_available_previews(), int)
