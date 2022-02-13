from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from pages.forms import SignUpForm
from .models import Profile

class CustomUserAdmin(UserAdmin):
    add_form = SignUpForm
    model = Profile
    list_display=['username','refresh_token','email','is_staff','is_superuser','is_active','bio','phone_number','birth_date','gender','is_doctor','verified','date_created','avatar']
    pass

admin.site.register(Profile, CustomUserAdmin)

##Maybe rework this later for better inclusion of all models.
from django.apps import apps
from django.contrib import admin

class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)

models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass