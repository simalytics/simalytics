from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('content_profiles.views',
    url(r'^$', 'content_profile_list', name='content_profiles_list'),
    url(r'^add$', 'content_profile_add', name='content_profile_add'),
    url(r'^view/(?P<id>[\d]+)/$', 'content_profile_view', name='content_profile_view'),
    url(r'^drop/(?P<id>[\d]+)/$', 'content_profile_drop', name='content_profile_drop'),
    url(r'^pcu/(?P<pcu_id>[\d]+)/view/$', 'pcu_view', name='pcu_view')
)
