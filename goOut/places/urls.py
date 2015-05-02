from django.conf.urls import patterns,  url

urlpatterns = patterns('places.views',
	
	# kefi labs llc home
	url(r'^kefiHome$', 'homeView', name='homeView'),	

	# kefi
	url(r'^kefi$', 'kefiHomeView', name='kefiHomeView'),	
	url(r'^kefi/getkefi$', 'getKefi', name='getKefi'),
	url(r'^kefi/getkefi/submit$', 'getKefi_submit', name='getKefi_submit'),
	url(r'^kefi/aboutUs$', 'aboutUs', name='aboutUs'),
	url(r'^kefi/redirectIOS$', 'redirectIOS', name='redirectIOS'),



	# assassins
	url(r'^assassins$', 'assassins', name='assassins'),	
	url(r'^assassins/terms$', 'assassins_terms', name='assassins_terms'),	
	url(r'^assassins/privacy$', 'assassins_privacy', name='assassins_privacy'),	


	# ripple
	url(r'^$', 'ripple', name='ripple'),
	url(r'^ripple$', 'ripple', name='ripple'),
	url(r'^Ripple$', 'ripple', name='ripple'),	
	url(r'^ripple/terms$', 'ripple_terms', name='ripple_terms'),	
	url(r'^ripple/privacy$', 'ripple_privacy', name='ripple_privacy'),
	url(r'^ambassador$', 'ripple_ambassador', name='ripple_ambassador'),
	url(r'^careers$', 'ripple_careers', name='ripple_careers'),


	####### v0 of Kefi app ########
	url(r'^v0$', 'getCurLoc', name='getCurLoc'),
	url(r'^index$', 'index', name='index'),
	url(r'^search/(?P<search_term>.+)/$', 'search', name='search'),
	url(r'^map/$', 'map', name='map'),
	
	
	url(r'^review$', 'submitReview', name='submitReview'),
	url(r'^review/(?P<place_name>.+)/(?P<reference>.+)/$', 'submitReviewVenue', name='submitReviewVenue'),
	url(r'^review/submit$', 'submit_submitReview', name='submit_submitReview'),
	
	#create user's own page, view other people's profile, and see user's favorited places
	url(r'^profile/(?P<user_id>.+)/$', 'view_profile', name='view_profile'),
	url(r'^fav/$', 'view_fav', name='view_fav'),
	
	url(r'^(?P<place_name>.+)/(?P<placeId>.+)/fav/$', 'add_fav', name='add_fav'),
		
	#detail page about a place
	url(r'^venue/(?P<place_id>.+)/$', 'placeDetail', name='placeDetail'),	

	url(r'^feedback$', 'feedback', name='feedback'),
	url(r'^feedback/submit$', 'feedback_submit', name='feedback_submit'),

	url(r'^about$', 'about', name='about'),

	url(r'^tag$', 'tag', name='tag'),

	url(r'^placeTagUpdate$', 'placeTagUpdate', name='placeTagUpdate'),

	url(r'^userTagUpdate$', 'userTagUpdate', name='userTagUpdate'),

	#url(r'^feedback$', 'feedback', name='feedback'),
	#url(r'^feedback/submit$', 'feedback_submit', name='feedback_submit'),
	#url(r'^(?P<joke_id>\d+)/up/$', 'up', name='up'),
	#url(r'^(?P<joke_id>\d+)/down/$', 'down', name='down'),
) 