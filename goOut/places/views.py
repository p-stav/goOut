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
from datetime import datetime
from places.models import UserProfile, Place, Hashtag, PlaceTag, UserAction
import sets
from math import exp, log10, floor
from collections import Counter
import oauth2

timeDecayExponent = 0.00001


##find today's date to find items close to it in db
#date = datetime.today()
#for testing purposes, hardcode datetime
date = datetime(2013, 12, 28, 22, 40, 41, 879000)
cutoffTime = datetime(date.year,date.month,date.day, date.hour-2, date.minute, date.second, date.microsecond)

def getCurLoc(request):
	context = {}
	return render(request, 'places/getCurLoc.html', context)
	
	
#index page. 
def index(request):
	#find curLong + curLat
	
	curLoc = request.POST['position']
	
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

	#for each place, do a check for id in curRevList, and append hashtag information
	#create two dictionaries to access for next view, one that have data for, one that we don't
	placeMatch = []
	placeNoMatch = []
	
	for place in venues:
		if place['id'] in curRevList:
			#iterate over curRev and find all instances to append to dict to append to json
			hashtags = {}
			for placeTag in curRev:
				if placeTag.place.placeID == place['id']:
					timeNow = datetime.today()
					timeDelta = timeNow - placeTag.lastUpdate
					placeTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
					placeTag.lastUpdate = timeNow
					placeTag.save()
					hashtags[placeTag.tag.text] = placeTag.score
					
			#TO-DO: create order of list
					
			#check if price_level and rating exist and append
			if 'rating' not in place.keys():
				place['rating'] = 'N/A'
			#if 'price_level' not in place.keys():
			#	place['price_level'] = 'N/A'
				
			#sort hashtag scores, and pick 3
			orderHashtags = Counter(hashtags)
			topTags = orderHashtags.most_common(3)
			topHashtags = [i[0] for i in topTags]
			
			#round distance, list of categories, and location
			distance = round(place['distance'] * 0.000621371192, -int(floor(log10(place['distance'] * 0.000621371192))))
			categories = [i[0] for i in place['categories']]
			try: location = place['location']['neighborhoods'][0]
			except: location=''

			temp = {'name': place['name'], 'id': place['id'], 'rating': place['rating_img_url'], 'types': categories, 'location': location, 'hashtags': topHashtags, 'distance':distance}
			
			#append
			placeMatch.append(temp)
		
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
			
			try: location=place['location']['neighborhoods'][0]
			except: location=''

			temp = {'name': place['name'], 'id': place['id'], 'rating': place['rating_img_url'], 'types': categories, 'address':address, 'location': location, 'distance':distance}
			
			
			#append
			placeNoMatch.append(temp)

	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
	else:
		userName = ''
	context = { 'userName':userName, 'placeMatch': placeMatch, 'placeNoMatch': placeNoMatch }
	return render(request, 'places/index.html', context)
	
	
def placeDetail(request,place_id):
	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
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
	#get PlaceTags in our database
	tags = PlaceTag.objects.filter(place__placeID= place['id'], lastUpdate__gte = cutoffTime)
	
	#send relevant information to templates
	#check to see if all keys exist. If not, assign 'NA' values
	if 'display_phone' not in place.keys():
		place['display_phone'] = 'N/A'
		
	if 'display_address' not in place['location'].keys():
		place['location']['display_address'] = 'N/A'
	
	if 'rating_img_url' not in place.keys():
		place['rating_img_url'] = 'N/A'
	
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
		timeNow = datetime.today()
		timeDelta = timeNow - placeTag.lastUpdate
		placeTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
		placeTag.lastUpdate = timeNow
		placeTag.save()

	#edit address:
	address = []
	address.append(place['location']['address'][0] + '  ' + place['location']['city'] + ',' + place['location']['state_code'])
	address.append(place['location']['cross_streets'] + ', ' + place['location']['neighborhoods'][0])

	categories = [i[0] for i in place['categories']]
	display_phone = place['display_phone'][3:]

	context = {'userName':userName, 'id':place['id'], 'tags':tags, 'name':place['name'], 'venueTypes':categories, 'address':address, 'phone': display_phone, 'rating':place['rating_img_url_small']}
	
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
	filterPlace = PlaceTag.objects.filter(place=newPlace, lastUpdate__gte = cutoffTime)
	
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
			placeTag.save()
			
			#add new User Action
			newAction = UserAction.objects.create(userID=curUser, time = datetime.today(), place = newPlace , tag = placeTag.tag)
			newAction.save()
			
	#create a new review with remaining tags that didn't match
	for hashtag in tags: 
		newVenueReview = PlaceTag.objects.create(place=newPlace, tag = Hashtag.objects.get(text=hashtag), freq=1, lastUpdate=datetime.today(), score = 50)
		
		#log new user action
		newAction = UserAction.objects.create(userID=curUser, time = datetime.today(), place = newPlace , tag = Hashtag.objects.get(text=hashtag))
		newAction.save()
		
		#update UserAction and UserProfile Points
		
		newVenueReview.save()
	
	#add a point to the user
	curUser.points += 1
	curUser.save()
	
	return HttpResponseRedirect('/')
		
		
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
		
	return HttpResponseRedirect('/')
	
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
