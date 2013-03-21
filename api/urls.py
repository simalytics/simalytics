from django.conf.urls.defaults import *
from django.conf import settings



urlpatterns = patterns('api.views',
    url(r'^opn/(?P<profile_id>[\d]+)$', 'api_operation_see', name='api_operation_see'),
    url(r'^opn/(?P<profile_id>[\d]+)/(?P<action_id>[\d]+)/$', 'api_operation_read', name='api_operation_read'),
    
    # Profile (administration):
    #url(r'^opn/profile/create$', 'api_operation_profile_create', name='api_operation_profile_create'),
    #url(r'^opn/profile/delete/(?P<profile_id>[\d]+)$', 'api_operation_profile_delete', name='api_operation_profile_delete'),
    
    # Guest session
    url(r'^opn/pcu/session$', 'api_operation_client_session_init', name='api_operation_client_session_init'),
    
    # PCU (administration):
    url(r'^opn/pcu/register$', 'api_operation_pcu_register', name='api_operation_pcu_register'),
    
    url(r'^opn/pcu/(?P<pcu_pub_key>[\w]+)/delete$', 'api_operation_pcu_delete', name='api_operation_pcu_delete'),

    url(r'^opn/pcu/all$', 'api_operation_pcu_list', name='api_operation_pcu_list'),
    
    url(r'^opn/pcu/(?P<pcu_pub_key>[\w]+)$', 'api_operation_pcu_get', name='api_operation_pcu_get'),

    url(r'^opn/pcu/(?P<pcu_pub_key>[\w]+)/overlay$', 'api_operation_render_overlay', name='api_operation_render_overlay'),
    
    # PCU access
    # NOTE: visits are really just another form of click.
    #url(r'^opn/pcu/(?P<pcu_pub_key>p[\w]+)/visit$', 'api_operation_pcu_visit', name='api_operation_pcu_visit'),
    url(r'^opn/pcu/(?P<pcu_pub_key>[\w]+)/click$', 'api_operation_pcu_click', name='api_operation_pcu_click')
)
