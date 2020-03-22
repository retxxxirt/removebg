from json import JSONDecodeError

import requests
from requests import Session, Response, HTTPError

from removebg.exceptions import APIError


def make_url(uri: str) -> str:
    return f'https://www.remove.bg/{uri}'


def make_api_url(uri: str) -> str:
    return f'https://api.remove.bg/v1.0/{uri}'


def make_request(method: str, url: str, session: Session = requests, **kwargs) -> Response:
    response = session.request(method, url, **kwargs)
    response.raise_for_status()

    return response


def make_uri_request(method: str, uri: str, session: Session = requests, **kwargs) -> Response:
    return make_request(method, make_url(uri), session, **kwargs)


def make_api_request(method: str, uri: str, api_token: str, **kwargs) -> Response:
    kwargs['headers'] = {**(kwargs.get('headers') or {}), 'X-Api-Key': api_token}

    try:
        return make_request(method, make_api_url(uri), **kwargs)
    except HTTPError as exception:
        try:
            raise APIError(exception.response.json()['errors'][0]['title'])
        except (JSONDecodeError, KeyError, IndexError):
            pass
        raise
