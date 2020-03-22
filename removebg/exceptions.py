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


class APIError(RemoveBgException):
    def __init__(self, error: str):
        super().__init__(f'API Error: {error}.')
