from collections import Callable

from removebg.exceptions import TokenRequired


def token_required(token_name: str):
    def decorator(method: Callable):
        def wrapper(client: object, *args, **kwargs):
            if getattr(client, f'_{token_name}_token') is None:
                raise TokenRequired(token_name)
            return method(client, *args, **kwargs)

        return wrapper

    return decorator
