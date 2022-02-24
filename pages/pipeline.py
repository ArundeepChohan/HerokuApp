from .models import Profile
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