from typing import Tuple

from bs4 import BeautifulSoup
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
from requests import Session

from .decorators import token_required
from .exceptions import AccountCreationFailed, LoginFailed
from .requests import make_uri_request, make_request, make_url, make_api_request


class RemoveBg:
    def __init__(self, removebg_token: str = None, anticaptcha_token: str = None):
        self._removebg_token = removebg_token
        self._anticaptcha_token = anticaptcha_token

    @staticmethod
    def activate_email(activation_link: str):
        make_request('GET', activation_link)

    def _preauth(self, action: str) -> Tuple[Session, str, str]:
        response = make_uri_request('GET', f'users/{action}', session := Session())
        soup = BeautifulSoup(response.content, 'html.parser')

        recaptcha_site_key = soup.select_one('.g-recaptcha')['data-sitekey']

        (solve_job := AnticaptchaClient(self._anticaptcha_token).createTask(
            NoCaptchaTaskProxylessTask(make_url(f'users/{action}'), recaptcha_site_key)
        )).join()

        authenticity_token = soup.select_one('[name="csrf-token"]')['content']
        recaptcha_token = solve_job.get_solution_response()

        return session, authenticity_token, recaptcha_token

    @token_required('anticaptcha')
    def create_account(self, email: str, password: str):
        session, authenticity_token, recaptcha_token = self._preauth('sign_up')

        response = make_uri_request('POST', 'users', session, data={
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'user[email]': email,
            'user[password]': password,
            'user[password_confirmation]': password,
            'user[terms_of_service]': 1,
            'user[receive_newsletter]': 0,
            'user[locale]': 'en',
            'g-recaptcha-response': recaptcha_token
        }, allow_redirects=False)

        if response.status_code != 302:
            raise AccountCreationFailed(email)

    @token_required('anticaptcha')
    def login(self, email: str, password: str) -> str:
        session, authenticity_token, recaptcha_token = self._preauth('sign_in')

        response = make_uri_request('POST', 'users/sign_in', session, data={
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'user[email]': email,
            'user[password]': password,
            'user[remember_me]': 0,
            'g-recaptcha-response': recaptcha_token
        }, allow_redirects=False)

        if response.status_code != 302:
            raise LoginFailed(email)

        response = make_uri_request('GET', 'profile', session)
        soup = BeautifulSoup(response.content, 'html.parser')

        self._removebg_token = soup.select_one('[data-hj-suppress]').text.strip()
        return self._removebg_token

    @token_required('removebg')
    def remove_background(self, **options) -> bytes:
        return make_api_request(
            'POST', 'removebg', self._removebg_token, data=options,
            files={k: options.pop(k) for k in ['image_file', 'bg_image_file'] if k in options},
        ).content

    @token_required('removebg')
    def remove_background_from_file(self, filepath: str, **options) -> bytes:
        with open(filepath, 'rb') as file:
            return self.remove_background(**{**options, 'image_file': file})

    @token_required('removebg')
    def remove_background_from_url(self, url: str, **options) -> bytes:
        return self.remove_background(**{**options, 'image_url': url})

    @token_required('removebg')
    def remove_background_from_base64(self, base64: str, **options) -> bytes:
        return self.remove_background(**{**options, 'image_file_b64': base64})
