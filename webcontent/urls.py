from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from webcontent import settings

admin.autodiscover()

urlpatterns = patterns('webcontent.core.controllers.landing',

    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^register/user/$', 'register_user', name='register_user'),
)

urlpatterns += patterns('webcontent.core.controllers.account',
    url(r'^settings/account/$', 'account_settings', name='account_settings'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

# XXX This is only an admin site so we are serving static files locally.
staticdir= settings.PROJECT_DIR + settings.BACKEND_DIR + "/static"
urlpatterns += patterns('', url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': staticdir}),)