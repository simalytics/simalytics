from django.conf.urls.defaults import *
from django.conf import settings



urlpatterns = patterns('api.views',
    url(r'^opn/(?P<profile_id>[\d]+)$', 'api_operation_see', name='api_operation_see'),
    url(r'^opn/(?P<profile_id>[\d]+)/(?P<action_id>[\d]+)/$', 'api_operation_read', name='api_operation_read'),
    
    # Profile (administration):
    #url(r'^opn/profile/create$', 'api_operation_profile_create', name='api_operation_profile_create'),
    #url(r'^opn/profile/delete/(?P<profile_id>[\d]+)$', 'api_operation_profile_delete', name='api_operation_profile_delete'),
    
    # PCU (administration):
    url(r'^opn/pcu/register$', 'api_operation_pcu_register', name='api_operation_pcu_register'),
    
    url(r'^opn/pcu/(?P<pcu_id>[\d]+)/delete$', 'api_operation_pcu_delete', name='api_operation_pcu_delete'),
    
    # PCU access
    url(r'^opn/pcu/(?P<pcu_id>p[\d]+)/visit$', 'api_operation_pcu_visit', name='api_operation_pcu_visit')
)
