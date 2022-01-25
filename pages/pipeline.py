from .models import Profile

def store_refresh_token(user=None, *args, **kwargs):
    extra_data = user.social_auth.get(provider="google-oauth2").extra_data
    Profile.objects.get_or_create(
        user=user, defaults={"refresh_token": extra_data["refresh_token"]}
    )