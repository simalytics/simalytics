from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('api.views',
    url(r'^opn/(?P<profile_id>[\d]+)$', 'api_operation_see', name='api_operation_see'),
    url(r'^opn/(?P<profile_id>[\d]+)/(?P<action_id>[\d]+)/$', 'api_operation_read', name='api_operation_read'),
)
