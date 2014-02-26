from django.conf.urls import patterns,  url

urlpatterns = patterns('places.views',
	
	#list of places, search page, and map
	url(r'^$', 'getCurLoc', name='getCurLoc'),
	url(r'^getCurLocHashtag$', 'getCurLocHashtag', name='getCurLocHashtag'),
	url(r'^index$', 'index', name='index'),
	url(r'^search/(?P<search_term>.+)/$', 'search', name='search'),
	url(r'^map/$', 'map', name='map'),
	
	
	url(r'^review$', 'submitReview', name='submitReview'),
	url(r'^review/(?P<place_name>.+)/(?P<reference>.+)/$', 'submitReviewVenue', name='submitReviewVenue'),
	url(r'^review/submit$', 'submit_submitReview', name='submit_submitReview'),
	
	#create user's own page, view other people's profile, and see user's favorited places
	url(r'^user/$', 'view_profile', name='profile'),
	url(r'^fav/$', 'view_fav', name='view_fav'),
	
	url(r'^(?P<place_name>.+)/(?P<placeId>.+)/fav/$', 'add_fav', name='add_fav'),
		
	#detail page about a place
	url(r'^venue/(?P<place_id>.+)/$', 'placeDetail', name='placeDetail'),	

	url(r'^feedback$', 'feedback', name='feedback'),
	url(r'^feedback/submit$', 'feedback_submit', name='feedback_submit'),

	url(r'^about$', 'about', name='about'),

	url(r'^tag/(?P<hashtag>.+)/$', 'tag', name='tag'),

	#url(r'^feedback$', 'feedback', name='feedback'),
	#url(r'^feedback/submit$', 'feedback_submit', name='feedback_submit'),
	#url(r'^(?P<joke_id>\d+)/up/$', 'up', name='up'),
	#url(r'^(?P<joke_id>\d+)/down/$', 'down', name='down'),
) 