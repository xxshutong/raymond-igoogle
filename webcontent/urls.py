from django.conf.urls.defaults import patterns, url
from webcontent import settings

urlpatterns = patterns('webcontent.core.controllers.landing',

    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^register/user/$', 'register_user', name='register_user'),
    url(r'^register/author/$', 'register_author', name='register_author'),
    url(r'^verify/member/(?P<user_id>\w+)/(?P<token>\w+)/$', 'register_verify', name='register_verify'),
)

urlpatterns += patterns('webcontent.core.controllers.account',
    url(r'^settings/email/$', 'email_settings', name='email_settings'),
    url(r'^settings/account/$', 'account_settings', name='account_settings'),
    url(r'^settings/author/list/$', 'ajax_get_author_handle', name='ajax_get_author_handle'),
    url(r'^settings/email/update/$', 'update_email_settings', name='update_email_settings'),
)

urlpatterns += patterns('webcontent.core.controllers.admin',
    url(r'^admin/$', 'login', name='admin_login'),
    url(r'^admin/logout/$', 'logout', name='admin_logout'),
    url(r'^admin/dashboard/$', 'dashboard', name='admin_dashboard'),
)

urlpatterns += patterns('webcontent.core.controllers.history',
)

# XXX This is only an admin site so we are serving static files locally.
staticdir= settings.PROJECT_DIR + settings.BACKEND_DIR + "/static"
urlpatterns += patterns('', url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': staticdir}),)
