from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from enhanced_accounts.signals import *

from enhanced_accounts.forms import EnhancedRegistrationForm, EnhancedLoginForm, EnhancedPasswordResetForm, EnhancedSetPasswordForm, EnhancedPasswordChangeForm
admin.autodiscover()


urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',

    (r'^$', 'enhanced_accounts.views.index'),

    (r'^admin/', include(admin.site.urls)),

    # todo: add '#_=_' redirection

    (r'^content_profiles/', include('content_profiles.urls')),

    (r'^api/', include('api.urls')),

    url(r'^accounts/register/$',
             'registration.views.register',
             {'form_class': EnhancedRegistrationForm,
              'backend':'registration.backends.default.DefaultBackend'},
             name='registration_register'),

    url(r'^accounts/login/$',
            'django.contrib.auth.views.login',
                 {'authentication_form':EnhancedLoginForm },
                 name='registration_login'),

    url(r'^accounts/password/reset/$',
            'django.contrib.auth.views.password_reset',
                 {'password_reset_form':EnhancedPasswordResetForm },
                 name='auth_password_reset'),

    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            'django.contrib.auth.views.password_reset_confirm',
                 {'set_password_form':EnhancedSetPasswordForm },
                 name='auth_password_reset_confirm'),

    url(r'^accounts/password/change/$',
            'django.contrib.auth.views.password_change',
                 {'password_change_form':EnhancedPasswordChangeForm },
                 name='auth_password_change'),


    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
                          {'next_page': '/'}),

    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'', include('social_auth.urls')),
)

