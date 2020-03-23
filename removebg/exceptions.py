from abc import ABC


class RemoveBgException(Exception):
    pass


class TokenRequired(RemoveBgException):
    def __init__(self, token_name: str):
        super().__init__(f'This method requires {token_name} token.')


class AccountCreationFailed(RemoveBgException):
    def __init__(self, email: str):
        super().__init__(f'Unable to create account for unknown reason. Account email: {email}.')


class LoginFailed(RemoveBgException):
    def __init__(self, email: str):
        super().__init__(f'Unable to login into account for unknown reason. Account email: {email}.')


class APIException(RemoveBgException, ABC):
    @property
    def status_code(self):
        raise NotImplementedError


class InvalidParameters(APIException):
    status_code = 400


class InsufficientCredits(APIException):
    status_code = 402


class AuthenticationFailed(APIException):
    status_code = 403


class RateLimitExceeded(APIException):
    status_code = 429
