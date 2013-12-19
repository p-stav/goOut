from django.conf.urls import patterns,  url

urlpatterns = patterns('places.views',
	
	#list of places and map
	url(r'^$', 'index', name='index'),
	url(r'^/map/$', 'index', name='index'),
	
	
	url(r'^submit$', 'submitReview', name='submitReview'),
	url(r'^submit/submit$', 'submit_submitReview', name='submit_submitReview'),
	
	url(r'^user/$', 'view_profile', {'username' : ''}),
	url(r'^user/(?P<username>.+)/$', 'view_profile', name='profile'),
	
	#detail page about a place
	url(r'^(?P<place_id>\d+)/$', 'placeDetail', name='detail'),
	
	#create list of favorited places to provide more information
	url(r'^(?P<joke_id>\d+)/fav/$', 'fav', name='fav'),
	
	
	
	#url(r'^user/fav$', 'view_fav', name='user_fav'),
	#url(r'^feedback$', 'feedback', name='feedback'),
	#url(r'^feedback/submit$', 'feedback_submit', name='feedback_submit'),
	#url(r'^(?P<joke_id>\d+)/up/$', 'up', name='up'),
	#url(r'^(?P<joke_id>\d+)/down/$', 'down', name='down'),
)