"""
WSGI config for myroutine project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os

from local_settings import *
from django.core.wsgi import get_wsgi_application
import base64
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myroutine.settings')

application = get_wsgi_application()

class AuthenticationMiddleware(object):
    def __init__(self, app, username, password):
        self.app = app
        self.username = username
        self.password = password
    def __unauthorized(self, start_response):
        start_response('401 Unauthorized', [
            ('Content-type', 'text/plain'),
            ('WWW-Authenticate', 'Basic realm="restricted"')
        ])
        return ['You are unauthorized and forbidden to view this resource.'.encode()]
    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO")
        if not ("api" in path or "admin" in path):
            return self.app(environ, start_response)
        
        authorization = environ.get('HTTP_AUTHORIZATION', None)
        if not authorization:
            return self.__unauthorized(start_response)

        (method, authentication) = authorization.split(' ', 1)
        if 'basic' != method.lower():
            return self.__unauthorized(start_response)

        authentication = base64.b64decode(authentication).decode("UTF-8")
        request_username, request_password = authentication.strip().split(':', 1)

        if str(self.username) == str(request_username) and str(self.password) == str(request_password):
            print("authorized")
            return self.app(environ, start_response)

        return self.__unauthorized(start_response)


application = AuthenticationMiddleware(application, BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD)
