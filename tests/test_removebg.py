import os
import warnings
from base64 import b64encode
from unittest import TestCase
from uuid import uuid4

import requests
from bs4 import BeautifulSoup
from tempmail import Tempmail

from removebg.exceptions import AccountCreationFailed, LoginFailed
from removebg.removebg import RemoveBg


class RemoveBgTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        warnings.simplefilter('ignore', ResourceWarning)

        cls.client = RemoveBg(
            os.environ.get('REMOVEBG_TOKEN'),
            os.environ.get('ANTICAPTCHA_TOKEN')
        )

        super().setUpClass()

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
            AccountCreationFailed, self.client.create_account,
            os.environ.get('REMOVEBG_USERNAME'), 'Pa$$w0rd'
        )

    def test_login(self):
        self.assertEqual(len(self.client.login(
            os.environ.get('REMOVEBG_USERNAME'),
            os.environ.get('REMOVEBG_PASSWORD')
        )), 24)

        self.assertRaises(
            LoginFailed, self.client.login,
            os.environ.get('REMOVEBG_USERNAME'), 'Pa$$w0rd'
        )

    def test_obtain_api_key(self):
        tempmail, password = Tempmail(), str(uuid4())[:16]
        self.client.create_account(tempmail.email, password)

        message = tempmail.wait_for('noreply@remove.bg')
        soup = BeautifulSoup(message['mail_html'], 'html.parser')

        self.client.activate_email(soup.select_one('.btn-primary')['href'])
        self.assertEqual(len(self.client.login(tempmail.email, password)), 24)
