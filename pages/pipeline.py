from functools import partial
from .models import Profile
from social_core.exceptions import  AuthException
def save_token(user,*args,**kwargs):
    extra_data = user.social_auth.get(provider="google-oauth2").extra_data

    profile, created = Profile.objects.get_or_create(
        username=user, defaults={"refresh_token": 
        extra_data["refresh_token"]}
    )

    # `created` will be false if the object exists
    if not created:
        profile.refresh_token = extra_data["refresh_token"]
        profile.save()
        
@partial
def associate_by_email(backend, details, user=None, *args, **kwargs):
    # No user 
    if user:
        return None

    email = details.get('email')
    if email:
        # Try to associate accounts registered with the same email address,
        # only if it's a single object. AuthException is raised if multiple
        # objects are returned.
        users = list(backend.strategy.storage.user.get_users_by_email(email))

        #That's the line you want to add
        active_users = [user for user in users if user.is_active]

        if len(active_users) == 0:
            return None
        elif len(active_users) > 1:
            raise AuthException(backend,'The given email address is associated with another account')
        else:
            return {'user': active_users[0],
                    'is_new': False}