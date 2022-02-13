from .models import Profile
def save_token(user,*args,**kwargs):
    extra_data = user.social_auth.get(provider="google-oauth2").extra_data
    print(extra_data["refresh_token"])
    Profile.objects.get_or_create(
        username=user, defaults={"refresh_token": extra_data["refresh_token"]}
    )