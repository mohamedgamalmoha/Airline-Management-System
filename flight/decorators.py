from typing import Callable
from functools import wraps, partial

from django.http.response import HttpResponseBadRequest

from accounts.models import User, Administrator


VALID_HTTP_METHODS = ('GET', 'POST', 'PUT', 'DELETE')

ERROR_RESPONSE_MESSAGES = {
    'invalid_http_method': 'Invalid HTTP Method, only ({}) are acceptable',
    'incorrect_http_method': 'Incorrect HTTP Method, It should be {}',
    'invalid_info_message': 'Invalid Data Info',
    'invalid_token_message': 'Invalid Token',
    'allow_admin_only': 'Only Admins Have permission To This View'
}


def login(username, password):
    user = User.objects.filter(username=username, password=password)
    if user.exists():
        return user.first()
    return None


def auth_view(view_func: Callable = None, method: str = None, messages: dict = None,
              allow_admin_only: bool = False):

    if view_func is None:
        return partial(auth_view, method=method, messages=messages, allow_admin_only=allow_admin_only)

    if messages is not ERROR_RESPONSE_MESSAGES:
        messages = {**ERROR_RESPONSE_MESSAGES, **messages} if messages is not None and isinstance(messages, dict) \
            else ERROR_RESPONSE_MESSAGES

    if method not in VALID_HTTP_METHODS:
        msg = messages.get('invalid_http_method', None)
        raise ValueError(msg.format(", ".join(VALID_HTTP_METHODS)))

    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.method != method:
            return HttpResponseBadRequest(messages.get('incorrect_http_method').format(method))

        if method == 'POST':
            username, password = request.POST.get('username'), request.POST.get('password')
        else:
            username, password = request.GET.get('username'), request.GET.get('password')

        user = login(username, password)
        if user:
            if allow_admin_only:
                admin = Administrator.objects.filter(user=user)
                if not admin:
                    return HttpResponseBadRequest(messages.get('allow_admin_only'))
            return view_func(request, *args, **kwargs)
        return HttpResponseBadRequest(messages.get('invalid_info_message'))

    return wrapper_func
