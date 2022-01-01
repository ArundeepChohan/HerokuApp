from django import forms
from django.core.files.images import get_image_dimensions
from pages.models import Profile
from django.contrib.auth.forms import UserCreationForm
from datetime import date, timedelta

class PickUserType(forms.Form):
    is_doctor = forms.BooleanField(required=False)

# verified = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'doctor'))
# from django.core.files.storage import FileSystemStorage

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
        
class UserProfileForm(forms.ModelForm):
    this_year = date.today().year
    year_range = [x for x in range(this_year - 100, this_year + 1)]
    bio = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 2,}),
    )
    birth_date = forms.DateField(
        label="What is your birth date?",
        widget=forms.SelectDateWidget(years=year_range),
    )
    class Meta:
        model = Profile
        fields = ('bio','phone_number','birth_date','avatar',)

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']

        today = date.today()
        first_date = today - timedelta(days=100 * 365)

        if not (first_date < birth_date <today):
            raise forms.ValidationError(u'Please select a date within the last 100 years')

        return birth_date

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']

        try:
            w, h = get_image_dimensions(avatar)

            #validate dimensions
            max_width = max_height = 1000
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                     '%s x %s pixels or smaller.' % (max_width, max_height))

            #validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                    'GIF or PNG image.')

            #validate file size
            if len(avatar) > (20 * 1024):
                raise forms.ValidationError(
                    u'Avatar file size may not exceed 20k.')

        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass

        return avatar