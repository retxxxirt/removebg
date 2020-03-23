from removebg import exceptions

WWW_ENDPOINT = 'https://www.remove.bg/'
API_ENDPOINT = 'https://api.remove.bg/v1.0/'

API_EXCEPTIONS = [
    exceptions.InvalidParameters,
    exceptions.InsufficientCredits,
    exceptions.AuthenticationFailed,
    exceptions.RateLimitExceeded
]
