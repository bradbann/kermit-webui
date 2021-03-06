from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#Discovering all widgets
if 'webui.widgets' in settings.INSTALLED_APPS:
    from widgets.loading import registry
    registry.discover_widgets()
    
    
from webui import initialize
initialize()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webui.views.home', name='home'),
    # url(r'^webui/', include('webui.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    (r'^grappelli/', include('grappelli.urls')),
    (r'^server/', include('webui.servers.urls')),
    (r'^restapi/', include('webui.restserver.urls')),
    (r'^puppetclasses/', include('webui.puppetclasses.urls')),
    (r'^agent/', include('webui.agent.urls')),
    (r'^index/(.*)', include('webui.index.urls')),
    (r'^messages/', include('webui.messages.urls')),
    (r'^platform/', include('webui.platforms.urls')),
    (r'^plugins/', include('webui.plugins.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'webui.index.views.logout_view'),
    (r'^export/', include('webui.exporter.urls')),
    (r'^auth/', include('webui.authentication.urls')),
    (r'^upload/', include('webui.upload.urls')),
    (r'^progress/', include('webui.progress.urls')),
    (r'^alerts/', include('webui.alerting.urls')),
    (r'^dynagroups/', include('webui.dynamicgroups.urls')),
    
    #(r'^chain/', include('webui.chain.urls')),
    #(r'^wsgroups/', include('a7x_wsgroups.urls')),
    
    (r'', include('webui.index.urls')),
)
