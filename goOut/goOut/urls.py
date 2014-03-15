from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'goOut.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

	url(r'', include('places.urls', namespace='places')),
    	
	#logging in capability, if we choose to include:
	
	url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/'}),
	url(r'^accounts/add/$', 'places.views.add_user', name='add_user'),
	url(r'^accounts/add/add$', 'places.views.add_user_add', name='add_user_add'),
	
	#admin
	url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
	
	#why can't we add create_user view here? Why is there not one?
)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
