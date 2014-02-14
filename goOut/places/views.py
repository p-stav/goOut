from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from urllib import urlopen
import json, pprint
from datetime import datetime, timedelta
from places.models import UserProfile, Place, Hashtag, PlaceTag, UserAction
import sets
from math import exp, log10, floor
from collections import Counter
import oauth2

timeDecayExponent = 0.00001


##find today's date to find items close to it in db
date = datetime.utcnow()
#for testing purposes, hardcode datetime
#date = datetime(2013, 12, 28, 22, 40, 41, 879000)
timeDeltaForCutoff = timedelta(hours=-2)
cutoffTime = date + timeDeltaForCutoff

minFontPercentage = 100
maxFontPercentage = 200
highestScore = 50

def getCurLoc(request):
	if request.POST.get('sortMethod'):
		method = request.POST['sortMethod']
	else: method = '0'

	if request.POST.get('searchTerm'):
		term = request.POST['searchTerm']
	else: term = ''

	context = {'sortMethod':method, 'search':term}

	return render(request, 'places/getCurLoc.html', context)
	
	
#index page. 
def index(request):
	#get curLong + curLat, or redirect to get info
	if request.POST.get('position'):
			curLoc = request.POST['position']
	else: return HttpResponseRedirect('/')


	if curLoc == '': #hardcode if fails.
		curLoc = '47.6159392,-122.3268701' #Seattle Pine/Bellevue
		#SF chestnut/VanNess.798542,-122.422345'	
	
	"""YELP API"""
	# Values for access
	consumer_key = 'nee5cvfcAEBHCg3wSGSdKw'
	consumer_secret = '3FmOuF9CLBGjyITGF66hbKmbgho'
	token = 'Ta-DBi45PaqkBhBnPJ1xpv1mmIjkVmxP'
	token_secret = 'ngCe85K7Xk6Sq37hI-4T-rE1Xtw'

	consumer = oauth2.Consumer(consumer_key, consumer_secret)
	sortMethod = request.POST.get('sortMethod')
	term = request.POST['search']
	

	if  term != '':
		url = 'http://api.yelp.com/v2/search?term=' + term + '&ll=' + curLoc
	elif sortMethod != '0':
		url = 'http://api.yelp.com/v2/search?term=nightlife&ll=' + curLoc +'&sort=' + sortMethod
	else:
		url = 'http://api.yelp.com/v2/search?term=nightlife&ll=' + curLoc
		

		
	
	oauth_request = oauth2.Request('GET', url, {})
	oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),'oauth_timestamp': oauth2.generate_timestamp(),'oauth_token': token, 'oauth_consumer_key': consumer_key})

	token = oauth2.Token(token, token_secret)
	oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signed_url = oauth_request.to_url()

	#grab json object from Yelp API
	req = urlopen(signed_url).read()
	venues = json.loads(req).get("businesses")

	"""GOOGLE PLACES API:

	apiCall = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+curLoc+"&radius=550&types=bar|casino|night_club&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0"

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	venues = json.loads(req).get("results")
	"""

	#grab array of reviews from our models
	curRev = PlaceTag.objects.filter(lastUpdate__gte = cutoffTime)
	curRevList = list(set([placeTag.place.placeID for placeTag in curRev]))
	
	#grab all other instances
	otherRev = PlaceTag.objects.filter(lastUpdate__lt = cutoffTime)
	otherRevList = list(set([placeTag.place.placeID for placeTag in otherRev]))

	#for each place, do a check for id in curRevList, and append hashtag information
	#create two dictionaries to access for next view, one that have data for, one that we don't
	placeMatch = []
	placeMatchOld = []
	placeNoMatch = []
	
	for place in venues:
		if place['id'] in curRevList:
			#iterate over curRev and find all instances to append to dict to append to json
			hashtags = {}
			for placeTag in curRev:
				if placeTag.place.placeID == place['id']:
					timeNow = datetime.utcnow()
					timeDelta = timeNow - placeTag.lastUpdate
					placeTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
					placeTag.lastUpdate = timeNow
					#placeTag.save()
					hashtags[placeTag.tag.text] = placeTag.score
					
			#sort hashtag scores, and pick 3
			orderHashtags = Counter(hashtags)
			topTags = orderHashtags.most_common(3)
			topHashtags = [i[0] for i in topTags]
			
			#check if price_level and rating exist and append
			if 'rating' not in place.keys():
				place['rating'] = 'N/A'
			#if 'price_level' not in place.keys():
			#	place['price_level'] = 'N/A'
			
			#round distance, list of categories, and location
			distance = round(place['distance'] * 0.000621371192, -int(floor(log10(place['distance'] * 0.000621371192))))
			categories = [i[0] for i in place['categories']]
			
			if 'image_url' not in place.keys():
				place['image_url']='hi'

			numRecentReviews = UserAction.objects.filter(place=Place.objects.get(placeID=place['id']), time__gte = cutoffTime)
			color = 'blue'
			if len(numRecentReviews) >= 5:
				color = 'red'
			elif len(numRecentReviews) >= 2:
				color = 'purple'

				
			temp = {'picture': place['image_url'] ,'name': place['name'], 'id': place['id'], 'types': categories, 'hashtags': topHashtags, 'distance':distance, 'color':color}
			
			#append
			placeMatch.append(temp)
		
		elif place['id'] in otherRevList:
			hashtags = {} #will show top two hashtags
			for placeTag in otherRev:
				if placeTag.place.placeID == place['id']:
					timeNow = datetime.utcnow()
					timeDelta = timeNow - placeTag.lastUpdate
					placeTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
					placeTag.lastUpdate = timeNow
					#placeTag.save()
					hashtags[placeTag.tag.text] = placeTag.score
					
			#sort hashtag scores, and pick 3
			orderHashtags = Counter(hashtags)
			topTags = orderHashtags.most_common(2)
			topHashtags = [i[0] for i in topTags]
								
			#check if price_level and rating exist and append
			if 'rating' not in place.keys():
				place['rating'] = 'N/A'
			#if 'price_level' not in place.keys():
			#	place['price_level'] = 'N/A'
			
			#round distance, list of categories, and location
			distance = round(place['distance'] * 0.000621371192, -int(floor(log10(place['distance'] * 0.000621371192))))
			categories = [i[0] for i in place['categories']]
			
			if 'image_url' not in place.keys():
				place['image_url']='hi'


				
			temp = {'picture': place['image_url'] ,'name': place['name'], 'id': place['id'], 'types': categories, 'hashtags': topHashtags, 'distance':distance, 'color':'blue'}
			
			#append
			placeMatchOld.append(temp)
			
		else:
			#check to see if price level and rating exist
			if 'rating' not in place.keys():
				place['rating'] = 'N/A'
			#if 'price_level' not in place.keys():
			#	place['price_level'] = 'N/A'

			#round distance, list of categories, and location
			distance = round(place['distance'] * 0.000621371192, -int(floor(log10(place['distance'] * 0.000621371192))))
			categories = [i[0] for i in place['categories']]
			address = []
			try: address.append(place['location']['address'][0])
			except: continue

			try: address.append(place['location']['cross_streets']) 
			except: continue
			
			if 'image_url' not in place.keys():
				place['image_url']='hi'

			temp = {'picture': place['image_url'], 'name': place['name'], 'id': place['id'], 'types': categories, 'address':address, 'distance':distance, 'color':'blue'}
			
			
			#append
			placeNoMatch.append(temp)

	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
	else:
		userName = ''
	context = { 'sort':sortMethod,'url':url, 'search':request.POST['search'], 'userName':userName, 'placeMatch': placeMatch, 'placeMatchOld':placeMatchOld, 'placeNoMatch': placeNoMatch, 'index':'index' }

	return render(request, 'places/index.html', context)
	
	
def placeDetail(request,place_id):
	placeFavorited = False
	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
		# check if user has favorited this place
		placeFavorited = curUser.favoritePlaces.filter(placeID=place_id).exists()

	else:
		userName = ''
	
	"""YELP API"""
	# Values for access
	consumer_key = 'nee5cvfcAEBHCg3wSGSdKw'
	consumer_secret = '3FmOuF9CLBGjyITGF66hbKmbgho'
	token = 'Ta-DBi45PaqkBhBnPJ1xpv1mmIjkVmxP'
	token_secret = 'ngCe85K7Xk6Sq37hI-4T-rE1Xtw'

	consumer = oauth2.Consumer(consumer_key, consumer_secret)
	url = 'http://api.yelp.com/v2/business/' + place_id
	
	oauth_request = oauth2.Request('GET', url, {})
	oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),'oauth_timestamp': oauth2.generate_timestamp(),'oauth_token': token, 'oauth_consumer_key': consumer_key})

	token = oauth2.Token(token, token_secret)
	oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signed_url = oauth_request.to_url()

	req = urlopen(signed_url).read()
	place = json.loads(req)
	

	"""
	apiCall = "https://maps.googleapis.com/maps/api/place/details/json?reference=" + place_id + "&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0"

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	place = json.loads(req).get("result")
	"""
	#####get PlaceTags in our database
	if len(PlaceTag.objects.filter(place__placeID= place['id'], lastUpdate__gte = cutoffTime)) >0:
		tags = PlaceTag.objects.filter(place__placeID= place['id'], lastUpdate__gte = cutoffTime).order_by('-score')
		oldTags=[]
	else:
	#len(PlaceTag.objects.filter(place__placeID= place['id'])) > 0:
		getOldTags = PlaceTag.objects.filter(place__placeID= place['id'],lastUpdate__lt = cutoffTime).order_by('-score')
		allOldTags = [i.tag.text for i in getOldTags]
		oldTags = []
		if len(allOldTags) >5:
			for i in range (0,5):
				oldTags.append(allOldTags[i])
		else:
			oldTags=allOldTags
		tags=[]
	#send relevant information to templates
	#check to see if all keys exist. If not, assign 'NA' values
	if 'display_phone' not in place.keys():
		place['display_phone'] = 'N/A'
		
	if 'display_address' not in place['location'].keys():
		place['location']['display_address'] = 'N/A'
	
	if 'rating_img_url' not in place.keys():
		place['rating_img_url'] = 'N/A'

	if 'review_count' not in place.keys():
		place['review_count'] = 'N/A'
	
	#if 'price_level' not in place.keys():
	#	place['price_level'] = 'N/A'
		
	#create address
	#address = []
	#address.append(place['address_components'][0]['long_name'] + ' ' + place['address_components'][1]['long_name'])
	#address.append(place['address_components'][2]['long_name'] + ',' + place['address_components'][3]['long_name'])
	
	#see if have info on opening times
	#try: place['open'] = place['opening_hours']['open_now']
	#except: place['open'] = ''
	
	#find what the most descriptive hashtags have been in the past?
	

	#update scores
	for placeTag in tags:
		timeNow = datetime.utcnow()
		timeDelta = timeNow - placeTag.lastUpdate
		placeTag.score *= exp(-1 * timeDecayExponent * timeDelta.total_seconds())
		placeTag.lastUpdate = timeNow
		#placeTag.save()


	#calculate font sizes
	fontSizes = []
	tagsFreq=[]
	totalScore = 0.0
	for placeTag in tags:
		fontSizePercentage = (placeTag.score / highestScore) * (maxFontPercentage - minFontPercentage) + minFontPercentage
		if fontSizePercentage > 400:
			fontSizePercentage = 400
		fontSizes.append(fontSizePercentage)

		venueTags = UserAction.objects.filter(place__placeID= place['id'], tag__text=placeTag.tag.text, time__gte = cutoffTime)
		tagsFreq.append(len(venueTags))

	tagsWithFonts = zip(tags, fontSizes, tagsFreq)


	#edit address:
	address = []
	if 'cross_streets' not in place['location'].keys():
		place['location']['cross_streets'] = ''
	if 'neighborhoods' not in place['location'].keys():
		place['location']['neighborhoods'] = ['','']
	
	address.append(place['location']['address'][0] + '  ' + place['location']['city'] + ',' + place['location']['state_code'])
	address.append(place['location']['cross_streets'] + ', ' + place['location']['neighborhoods'][0])

	categories = [i[0] for i in place['categories']]
	display_phone = place['display_phone'][3:]

	context = {'userName':userName, 'id':place['id'], 'oldTags':oldTags, 'tagsWithFonts':tagsWithFonts, 'name':place['name'], 'venueTypes':categories, 'address':address, 'phone': display_phone, 'rating':place['rating_img_url_small'], 'review_count':place['review_count'], 'placeFavorited':placeFavorited}
	
	return render(request, 'places/placeDetail.html', context)

#later, we will merge submitReview and submitReviewVenue to one view. It's a simple if statement to fix in a template file	
@login_required()
def submitReview(request):
	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
	else:
		userName = ''
		
	#grab all hashtags to display
	tags = Hashtag.objects.all()
	
	context = {'userName':userName,'tags':tags}
	return render(request, 'places/submitReview.html', context)

@login_required()
def submitReviewVenue(request, place_name, reference):
	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
	else:
		userName = ''
	
	#grab all hashtags to display
	tags = Hashtag.objects.all()
	
	context = {'userName':userName, 'tags':tags, 'id':reference, 'name':place_name}
	return render(request, 'places/submitReviewVenue.html', context)

	
def submit_submitReview(request):
	curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))

	#Check if place exists. If not, add place
	if Place.objects.filter(placeID=request.POST['venueId']).exists():
		newPlace = Place.objects.get(placeID=request.POST['venueId'])
	else:
		newPlace = Place.objects.create(placeID = request.POST['venueId'], placeName=request.POST['venueName'])
		newPlace.save()

	# Check if user recently reviewed this place (in last cutoff time)
	recentUserActions = UserAction.objects.filter(place=newPlace, userID=curUser, time__gte = cutoffTime)

	#if recentUserActions:
	#	return HttpResponseRedirect('/')


	
	#get list of tags
	#listTags = request.body
	tags = request.POST.getlist('tagNames')
	"""[]
	tagCount = 0
	tagName = 'tag'+str(tagCount)
	while (tagName in request.POST):
		tags.append(request.POST[tagName])
		tagCount += 1
		tagName = 'tag' + str(tagCount)
	"""

	#Filter for all instances of Places with same placeId and tag within alotted time
	filterPlace = PlaceTag.objects.filter(place=newPlace)
	
	if len(filterPlace)>0:
		#check to see if tag exists
		for placeTag in filterPlace:
			if placeTag.tag.text in tags:
				placeTag.freq += 1

				#update score
				timeNow = datetime.today()
				timeDelta = timeNow - placeTag.lastUpdate
				placeTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
				placeTag.score += 50
				placeTag.lastUpdate = timeNow

				#take out hashtag from the list
				position = tags.index(placeTag.tag.text)
				tags.pop(position)


				#add new User Action
				newAction = UserAction.objects.create(userID=curUser, time = datetime.today(), place = newPlace , tag = placeTag.tag)
				newAction.save()
				placeTag.save()

			
	#create a new review with remaining tags that didn't match
	for hashtag in tags: 
		newVenueReview = PlaceTag.objects.create(place=newPlace, tag = Hashtag.objects.get(text=hashtag), freq=1, lastUpdate=datetime.today(), score = 50)
		
		#log new user action
		newAction = UserAction.objects.create(userID=curUser, time = datetime.today(), place = newPlace , tag = Hashtag.objects.get(text=hashtag))
		newAction.save()
		

		newVenueReview.save()
	
	#add a point to the user
	curUser.points += 1
	curUser.save()

	redirectURL = '/venue/' + request.POST['venueId']

	return HttpResponseRedirect(redirectURL)
		
		
def add_user(request):
	context = { }
	return render(request, 'registration/add_user.html', context)
	
def add_user_add(request):
	try:
		newUser = User.objects.create(username=request.POST['uname'])
		newUser.set_password(request.POST['pwd'])
		# newUser.last_name = request.POST['last_name']
		# newUser.first_name = request.POST['first_name']

		# add to UserProfiles
		newUser.save()

		#temp = User.objects.get(username=request.POST['uname'])
		addUserProf = UserProfile(user=newUser, points=0)
		addUserProf.save()
		
		#add user to session
		auth = authenticate(username=request.POST['uname'], password=request.POST['pwd'])
		login(request, auth)
		return HttpResponseRedirect('/')
	
	except:
		error=1
		context = {'error':error}
		return render(request, 'registration/add_user.html', context)
	
	
	
@login_required()
def view_fav(request):

	curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
	userName = curUser.user.username
	
	favorites = curUser.favoritePlaces.all()
	
	favList = []
	
	for venue in favorites:
		hashtags = {}
		temp = PlaceTag.objects.filter(place=venue, lastUpdate__gte=cutoffTime)

		for i in temp:
			hashtags[i.tag.text]=i.score
	


		#before submit hashtag list, change to list of top 3:
		orderHashtags = Counter(hashtags)
		topTags = orderHashtags.most_common(3)
		topHashtags = [i[0] for i in topTags]
		#create dictionsary to append to list
		
		addToList = {'userName':userName, 'name':venue.placeName , 'hashtags':topHashtags, 'id':venue.placeID}
		
		favList.append(addToList)
	
	
	
	context = {'favorites':favList, 'user':curUser.user.username}
	
	return render(request, 'places/view_fav.html', context)
		
@login_required()
def add_fav(request, place_name, placeId):
	curUser=UserProfile.objects.get(user=User.objects.get(id=request.user.id))

	#check if place exists; if not, add!
	if Place.objects.filter(placeID=placeId).exists():
		current_venue = Place.objects.get(placeID = placeId)
	else: #add place
		current_venue = Place.objects.create(placeID=placeId, placeName=place_name)
		current_venue.save()

	if curUser.favoritePlaces.filter(id=current_venue.id).exists():
		curUser.favoritePlaces.remove(current_venue)
	else:
		curUser.favoritePlaces.add(current_venue)
	curUser.save()
		
	return HttpResponseRedirect('/venue/'+placeId+'/')
	
@login_required()	
def view_profile(request):
	#get username, favorites list, last activity
	curUser=UserProfile.objects.get(user=User.objects.get(id=request.user.id))
	userName = curUser.user.username
	
	#last places reviewed, in order of time 
	lastVisited = UserAction.objects.filter(userID=User.objects.get(id=request.user.id)).order_by('-time', 'tag__text')
	
	#get list of last 5 Places reviewed 
	count=0
	unique=0
	placeList = []
	
	while (count<len(lastVisited)):
		if unique>=5:
			break		
			
		if lastVisited[count].place.placeName not in placeList:
			placeList.append(lastVisited[count].place.placeName)
			unique += 1
			
		count +=1 # in case there are less than five unique places visited. 
	
	context = {'userName':userName,'firstName': curUser.user.first_name, 'favorites':placeList}
	return render(request, 'places/view_profile.html', context)
	
def search(request):
	context = {}
	return render(request, 'places/search', context)
	
	
def map(request):
	context = {}
	return render(request, 'places/maps', context)
