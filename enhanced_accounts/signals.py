from registration.signals import user_activated, user_registered
from django.contrib.auth import login
from django.conf import settings

def login_on_activation(sender, user, request, **kwargs):
    user.backend='django.contrib.auth.backends.ModelBackend'
    login(request,user)

user_activated.connect(login_on_activation)

#def create_empty_profile(sender, user, request, **kwargs):
#    new_profile = CustomUserProfile(user= user, invites_num = settings.INVITE_PER_USER)
#    new_profile.save()
#    existed_code = InviteItem.objects.get(code=request.POST['invite_code'])
#    existed_code.assigned_to = user
#    existed_code.active = False
#    existed_code.save()
#
#user_registered.connect(create_empty_profile)
