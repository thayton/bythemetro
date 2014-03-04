from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('bythemetro.views',
    (r'^$', 'main_page'),
    (r'^map/$', 'map'),
    (r'^table/$', 'table'),

    (r'^user/(?P<user_id>\d+)/$', 'user_page'),
    (r'^alerts/$', 'alerts'),
    (r'^create_alert/$', 'create_alert'),
    (r'^alert/(?P<alert_id>\d+)/$', 'alert_detail'),
    (r'^alert/(?P<alert_id>\d+)/edit/$', 'edit_alert'),
    (r'^alert/(?P<alert_id>\d+)/delete/$', 'delete_alert'),

    (r'^logout/$', 'logout_page'),
    (r'^register/$', 'register_page'),
)
