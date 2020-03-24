from typing import Tuple

from bs4 import BeautifulSoup
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
from requests import Session

from . import exceptions
from .decorators import token_required
from .requests import make_uri_request, make_request, make_url, make_api_request


class RemoveBg:
    def __init__(self, api_token: str = None, session_token: str = None, anticaptcha_token: str = None):
        self.api_token = api_token
        self.session_token = session_token
        self.anticaptcha_token = anticaptcha_token

    @token_required('anticaptcha')
    def _preauth(self, action: str) -> Tuple[Session, str, str]:
        response = make_uri_request('GET', f'users/{action}', session := Session())
        soup = BeautifulSoup(response.content, 'html.parser')

        recaptcha_site_key = soup.select_one('.g-recaptcha')['data-sitekey']

        (solve_job := AnticaptchaClient(self.anticaptcha_token).createTask(
            NoCaptchaTaskProxylessTask(make_url(f'users/{action}'), recaptcha_site_key)
        )).join()

        authenticity_token = soup.select_one('[name="csrf-token"]')['content']
        recaptcha_token = solve_job.get_solution_response()

        return session, authenticity_token, recaptcha_token

    @token_required('anticaptcha')
    def _login_credentials(self, email: str, password: str):
        session, authenticity_token, recaptcha_token = self._preauth('sign_in')

        response = make_uri_request('POST', 'users/sign_in', session, data={
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'user[email]': email,
            'user[password]': password,
            'user[remember_me]': 1,
            'g-recaptcha-response': recaptcha_token
        }, allow_redirects=False)

        if response.status_code != 302:
            raise exceptions.LoginFailed(email)

        self.session_token = session.cookies.get('remember_user_token')

    @token_required('session')
    def _get_profile(self) -> BeautifulSoup:
        response = make_uri_request('GET', 'profile', headers={
            'cookie': f'remember_user_token={self.session_token}'
        })

        if not response.url.endswith('/profile'):
            raise exceptions.SessionExpired()

        return BeautifulSoup(response.content, 'html.parser')

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
            raise exceptions.AccountCreationFailed(email)

    @staticmethod
    def activate_email(activation_link: str):
        make_request('GET', activation_link)

    def login(self, email: str = None, password: str = None, session_token: str = None):
        if session_token is None:
            self._login_credentials(email, password)
        else:
            self.session_token = session_token

        self.api_token = self._get_profile().select_one('[data-hj-suppress]').text.strip()

    @token_required('session')
    def get_available_credits(self) -> float:
        return float(self._get_profile().select_one('.profile-credit-balance').parent.text.strip())

    @token_required('session')
    def get_available_previews(self) -> int:
        parent_element = self._get_profile().select_one('.profile-balance-arrow').parent
        return int(parent_element.select('.row > div')[-1].text.strip().split()[0])

    @token_required('api')
    def remove_background(self, **options) -> bytes:
        return make_api_request(
            'POST', 'removebg', self.api_token, data=options,
            files={k: options.pop(k) for k in ['image_file', 'bg_image_file'] if k in options},
        ).content

    @token_required('api')
    def remove_background_from_file(self, filepath: str, **options) -> bytes:
        with open(filepath, 'rb') as file:
            return self.remove_background(**{**options, 'image_file': file})

    @token_required('api')
    def remove_background_from_url(self, url: str, **options) -> bytes:
        return self.remove_background(**{**options, 'image_url': url})

    @token_required('api')
    def remove_background_from_base64(self, base64: str, **options) -> bytes:
        return self.remove_background(**{**options, 'image_file_b64': base64})
