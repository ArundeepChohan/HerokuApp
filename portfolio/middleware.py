from django.contrib.auth import logout
import datetime

from settings import SESSION_IDLE_TIMEOUT


class SessionIdleTimeout(object):
    """Middle ware to ensure user gets logged out after defined period if inactvity."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_datetime = datetime.datetime.now()
            if 'last_active_time' in request.session:
                idle_period = (current_datetime - request.session['last_active_time']).seconds
                if idle_period > SESSION_IDLE_TIMEOUT:
                    logout(request, 'login.html')
            request.session['last_active_time'] = current_datetime

        response = self.get_response(request)
        return response