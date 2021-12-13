from django.contrib.auth import logout
from django.contrib import messages
import datetime
from django.shortcuts import redirect
from django.conf import settings


class SessionIdleTimeout:
    def process_request(self, request):
        if request.user.is_authenticated():
            current_datetime = datetime.datetime.now()
            if ('last_login' in request.session):
                last = (current_datetime - request.session['last_login']).seconds
                if last > settings.SESSION_IDLE_TIMEOUT:
                    logout(request, 'home.html')
            else:
                request.session['last_login'] = current_datetime
        return None