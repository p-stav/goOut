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
from places.models import UserProfile, Place, Hashtag, PlaceTag, UserAction, UserFeedback, UserTag
import sets
from math import exp, log10, floor, trunc
from collections import Counter
import oauth2

timeDecayExponent = 0.00001

##find today's date to find items close to it in db
#for testing purposes, hardcode datetime
#date = datetime(2013, 12, 28, 22, 40, 41, 879000)

minFontPercentage = 100
maxFontPercentage = 150
highestScore = 50
initialScore = 50

CategoryBlacklist = ['4bf58dd8d48988d1e0931735',
'4bf58dd8d48988d1d5941735']



def getCurLoc(request):
	if request.POST.get('sortMethod'):
		method = request.POST['sortMethod']
	else: method = '0'

	if request.POST.get('searchTerm'):
		term = request.POST['searchTerm']
	else: term = ''


	context = {'sortMethod':method, 'search':term}


	return render(request, 'places/getCurLoc.html', context)


def getCurLocHashtag(request):

	context = {'hashtag':request.POST.get('hashtag')}

	return render(request, 'places/getCurLocHashtag.html', context)

	
	
#index page. 
def index(request):
	#find today's date to find items close to it in db                                                                                                                                  
	date = datetime.utcnow()
	#for testing purposes, hardcode datetime                                                                                                                                             
	#date = datetime(2013, 12, 28, 22, 40, 41, 879000)                                                                                                                                   
	timeDeltaForCutoff = timedelta(hours=-2)
	cutoffTime = date + timeDeltaForCutoff
	#get curLong + curLat, or redirect to get info
	if request.POST.get('position'):
		curLoc = request.POST['position']
	else: return HttpResponseRedirect('/')


	if curLoc == '': #hardcode if fails.
		curLoc = '47.6159392,-122.3268701' #Seattle Pine/Bellevue
		#SF chestnut/VanNess.798542,-122.422345'

	client_id = 'T4XPWMEQAID11W0CSQLCP2P0NXGEUSDZRV4COSBJH2QEMC2O'
	client_secret = '0P1EQQ3NH102D0R3GNGTG0ZAL0S5T41YDB2NPOOMRMO2I2EO'
	category_id =  '4bf58dd8d48988d116941735,50327c8591d4c4b30a586d5d,4bf58dd8d48988d11e941735,4bf58dd8d48988d118941735,4bf58dd8d48988d1d8941735,4bf58dd8d48988d120941735,4bf58dd8d48988d121941735,4bf58dd8d48988d11f941735,4bf58dd8d48988d11b941735,4bf58dd8d48988d1d4941735,4bf58dd8d48988d11d941735,4bf58dd8d48988d122941735,4bf58dd8d48988d123941735'
	radius = '1000'	

	term = request.POST.get("search","")

	url = 'https://api.foursquare.com/v2/venues/search?ll=' + curLoc + '&radius=' + radius + '&intent=browse&categoryId=' + category_id 
	url += '&client_id=' + client_id + '&client_secret=' + client_secret + '&v=20140306'

	if term != '':
		url += '&query=' + term

	req = urlopen(url).read()
	venues = json.loads(req).get("response").get("venues")
	

	#check for sortMethod tag to sort by distance
	sortMethod = request.POST.get('sortMethod')
	if sortMethod != '0':
		venues = sorted(venues, key=lambda k: k['location']['distance'])

		
	"""YELP API"""
	# Values for access
	"""consumer_key = 'nee5cvfcAEBHCg3wSGSdKw'
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
	venues = json.loads(req).get("businesses")"""



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

	# Remove venues with categories on the blacklist
	venues = [place for place in venues if not isBlacklistedCategory(place)]

	
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
			topTags = orderHashtags.most_common(5)
			topHashtags = [i[0] for i in topTags]
			
			#check if price_level and rating exist and append
			#if 'rating' not in place.keys():
			#	place['rating'] = 'N/A'
			#if 'price_level' not in place.keys():
			#	place['price_level'] = 'N/A'
			
			#round distance, list of categories, and location
			distance = round(place['location']['distance'] * 0.000621371192, -int(floor(log10(place['location']['distance'] * 0.000621371192))))
			category = place['categories'][0]['name']
			
			image_url = place['categories'][0]['icon']['prefix'] + '64' + place['categories'][0]['icon']['suffix']

			color=getColorTheme(place['id'])

				
			temp = {'picture': image_url ,'name': place['name'], 'id': place['id'], 'types': category, 'hashtags': topHashtags, 'distance':distance, 'color':color}
			
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
			topTags = orderHashtags.most_common(5)
			topHashtags = [i[0] for i in topTags]
								
			#check if price_level and rating exist and append
			#if 'rating' not in place.keys():
			#	place['rating'] = 'N/A'
			#if 'price_level' not in place.keys():
			#	place['price_level'] = 'N/A'
			
			#round distance, list of categories, and location
			distance = round(place['location']['distance'] * 0.000621371192, -int(floor(log10(place['location']['distance'] * 0.000621371192))))
			category = place['categories'][0]['name']
			
			image_url = place['categories'][0]['icon']['prefix'] + '64' + place['categories'][0]['icon']['suffix']


				
			temp = {'picture': image_url ,'name': place['name'], 'id': place['id'], 'types': category, 'hashtags': topHashtags, 'distance':distance, 'color':'46,117,182'}
			
			#append
			placeMatchOld.append(temp)
			
		else:
			#check to see if price level and rating exist
			##if 'rating' not in place.keys():
			#	place['rating'] = 'N/A'
			#if 'price_level' not in place.keys():
			#	place['price_level'] = 'N/A'

			#round distance, list of categories, and location
			distance = round(place['location']['distance'] * 0.000621371192, -int(floor(log10(place['location']['distance'] * 0.000621371192))))
			category = category = place['categories'][0]['name']
			#address = []
			"""try: address.append(place['location']['address'][0])
			except: continue

			try: address.append(place['location']['cross_streets']) 
			except: continue
			"""
			image_url = place['categories'][0]['icon']['prefix'] + '64' + place['categories'][0]['icon']['suffix']

			temp = {'picture': image_url, 'name': place['name'], 'id': place['id'], 'types': category, 'distance':distance, 'color':'127,127,127'}
			
			
			#append
			placeNoMatch.append(temp)

	#get all hashtags to display
	tags = Hashtag.objects.all()

	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
	else:
		userName = ''

	sortMethod = ''
	context = {'tags':tags, 'sort':sortMethod, 'url':url, 'search':term, 'userName':userName, 'placeMatch': placeMatch, 'placeMatchOld':placeMatchOld, 'placeNoMatch': placeNoMatch, 'headerUIAdditions':'hi' }


	return render(request, 'places/index.html', context)
	
	
def placeDetail(request,place_id):
	##find today's date to find items close to it in db                                                                                                                                  
	date = datetime.utcnow()
	#for testing purposes, hardcode datetime                                                                                                                                             
	#date = datetime(2013, 12, 28, 22, 40, 41, 879000)                                                                                                                                   
	timeDeltaForCutoff = timedelta(hours=-2)
	cutoffTime = date + timeDeltaForCutoff
	placeFavorited = False
	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
		# check if user has favorited this place
		placeFavorited = curUser.favoritePlaces.filter(placeID=place_id).exists()

	else:
		userName = ''
	
	client_id = 'T4XPWMEQAID11W0CSQLCP2P0NXGEUSDZRV4COSBJH2QEMC2O'
	client_secret = '0P1EQQ3NH102D0R3GNGTG0ZAL0S5T41YDB2NPOOMRMO2I2EO'
	category_id = '4d4b7105d754a06376d81259'	

	#url = 'https://api.foursquare.com/v2/venues/50f1027ee4b04196702b9cb8?ll=47.6159392,-122.3268701&client_id=T4XPWMEQAID11W0CSQLCP2P0NXGEUSDZRV4COSBJH2QEMC2O&client_secret=0P1EQQ3NH102D0R3GNGTG0ZAL0S5T41YDB2NPOOMRMO2I2EO&v=20140229'
	url = 'https://api.foursquare.com/v2/venues/' + place_id + '?client_id=' + client_id + '&client_secret=' + client_secret + '&v=20140306'

	req = urlopen(url).read()
	place = json.loads(req).get("response").get("venue")

	"""YELP API"""
	# Values for access
	"""consumer_key = 'nee5cvfcAEBHCg3wSGSdKw'
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
	place = json.loads(req)"""

	

	"""
	apiCall = "https://maps.googleapis.com/maps/api/place/details/json?reference=" + place_id + "&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0"

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	place = json.loads(req).get("result")
	"""
	#####get PlaceTags and UserTags in our database
	if len(PlaceTag.objects.filter(place__placeID= place['id'], lastUpdate__gte = cutoffTime)) or len(UserTag.objects.filter(place__PlaceID=place['id'], lastUpdate__gte = cutoffTime)) >0:
		tags = PlaceTag.objects.filter(place__placeID= place['id'], lastUpdate__gte = cutoffTime).order_by('-score')
		userTags = UserTag.objects.filter(place__placeID=place['id'], lastUpdate__gte=cutoffTime).order_by('-score')

		oldTags=[]
	else: #no PlaceTags or UserTags
		getOldTags = PlaceTag.objects.filter(place__placeID= place['id'],lastUpdate__lt = cutoffTime).order_by('-score')
		allOldTags = [i.tag.text for i in getOldTags]
		oldTags = []

		if len(allOldTags) >5:
			for i in range (0,5):
				oldTags.append(allOldTags[i])
		else:
			oldTags=allOldTags
		
		tags=[]
		userTags=[]

	#send relevant information to templates
	#check to see if all keys exist. If not, assign 'NA' values

	#Place userTags and tags data in same lists. Define fontSizes and frequenceis
	allTags = []

	for tag in tags:
		tagObject = {}
		tagObject["tagText"] = tag.tag.text
		tagObject["freq"] = tag.freq
		tagObject["score"] = tag.score
		tagObject["lastUpdate"] = tag.lastUpdate

		allTags.append(tagObject)

	for tag in userTags:
		tagObject = {}
		tagObject["tagText"] = tag.tag
		tagObject["freq"] = tag.freq
		tagObject["score"] = tag.score
		tagObject["lastUpdate"] = tag.lastUpdate

		allTags.append(tagObject)
		

	#sort allTags in order of score
	allTags.sort(key=lambda x:x['score'])

	#update scores
	timeNow = datetime.utcnow()
	for placeTag in allTags:
		timeDelta = timeNow - placeTag["lastUpdate"]
		placeTag["score"] *= exp(-1 * timeDecayExponent * timeDelta.total_seconds())
		placeTag["lastUpdate"] = timeNow
		#placeTag.save()

	#define lists to zip together
	tags = []
	fontSizes = []
	tagsFreq =[]

	#calculate + grab font sizes, freq and tags
	totalScore = 0.0
	for placeTag in allTags:
		tags.append(placeTag["tagText"])

		fontSizePercentage = (placeTag["score"] / highestScore) * (maxFontPercentage - minFontPercentage) + minFontPercentage
		if fontSizePercentage > 220:
			fontSizePercentage = 220
		fontSizes.append(fontSizePercentage)
	
		#grab frequency
		
		#userActionsCorrectTag = placeTag["tag"].useraction_set.filter(place__placeID= place['id'], time__gte = cutoffTime)
		#venueTags = UserAction.objects.filter(place__placeID= place['id'], tag__text=placeTag.tag.text, time__gte = cutoffTime)
		#tagsFreq.append(len(userActionsCorrectTag))

		tagsFreq.append(placeTag["freq"])

	tagsWithFonts = zip(tags, fontSizes, tagsFreq)


	#edit address:
	#address = []
	#if 'cross_streets' not in place['location'].keys():
	#	place['location']['cross_streets'] = ''
	#if 'neighborhoods' not in place['location'].keys():
	##	place['location']['neighborhoods'] = ['','']
	
	#address.append(place['location']['address'][0] + '  ' + place['location']['city'] + ',' + place['location']['state_code'])
	#address.append(place['location']['cross_streets'] + ', ' + place['location']['neighborhoods'][0])
	address  = []

	if 'address' in place['location'].keys():
		address.append(place['location']['address'])
	if 'crossStreet' in place['location'].keys():
		address.append(place['location']['crossStreet'])
	category = category = place['categories'][0]['name']

	image_url = place['categories'][0]['icon']['prefix'] + '64' + place['categories'][0]['icon']['suffix']

	#get color theme
	color=getColorTheme(place['id'])

	#get comments from last two hours
	"""
	comments=[]
	if Place.objects.filter(placeID=place['id']).exists():
		comments = UserComment.objects.filter(Place=Place.objects.get(placeID=place['id']), time__gte=cutoffTime)

	commentTimestamps = []
	for comment in comments:
		commentTime = comment.time
		timeDifference = date - commentTime
		timeDifference = timeDifference.total_seconds()
		timestampString = 'Just now!'
		if timeDifference > 60:
			timeDifference /= 60
			timestampString = str(trunc(timeDifference)) + ' min ago'
			if timeDifference > 60:
				timeDifference /= 60
				timestampString = str(trunc(timeDifference)) + ' hr ago'
		commentTimestamps.append(timestampString)

	comments = zip(comments,commentTimestamps)

	comments.reverse()
	"""
	#get all hashtags to display on header
	tags = Hashtag.objects.all()

	context = {'userName':userName, 'id':place['id'], 'oldTags':oldTags, 'tagsWithFonts':tagsWithFonts, 'name':place['name'], 'venueTypes':category, 'address':address, 'placeFavorited':placeFavorited, 'color':color, 'picture' : image_url, 'comments':comments, 'tags':tags}
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
	
	#get color theme
	color=getColorTheme(reference)

	#grab all hashtags to display
	tags = Hashtag.objects.all()
	
	context = {'userName':userName, 'tags':tags, 'id':reference, 'name':place_name, 'color':color}
	return render(request, 'places/submitReviewVenue.html', context)

	
def submit_submitReview(request):
	##find today's date to find items close to it in db                                                                                                                                  
	date = datetime.utcnow()
	#for testing purposes, hardcode datetime                                                                                                                                             
	#date = datetime(2013, 12, 28, 22, 40, 41, 879000)                                                                                                                                   
	timeDeltaForCutoff = timedelta(hours=-2)
	cutoffTime = date + timeDeltaForCutoff
	curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))

	#Check if place exists. If not, add place
	if Place.objects.filter(placeID=request.POST['venueId']).exists():
		newPlace = Place.objects.get(placeID=request.POST['venueId'])
	else:
		newPlace = Place.objects.create(placeID = request.POST['venueId'], placeName=request.POST['venueName'])
		newPlace.save()

	###Do we want to dissallow user from reviewing multiple times in window?
	#Check if user recently reviewed this place (in last cutoff time)
	"""
	recentUserActions = UserAction.objects.filter(place=newPlace, userID=curUser, time__gte = cutoffTime)

	if recentUserActions:
		return HttpResponseRedirect('/')
	"""

	
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

	# check if existing UserAction otherwise add new one
	#for testing purposes, hardcode datetime                                                                                                                                             
	#date = datetime(2013, 12, 28, 22, 40, 41, 879000)                                                                                                                                   
	timeDeltaForUserActionCutoff = timedelta(minutes=-5)
	cutoffUserActionTime = date + timeDeltaForUserActionCutoff
	existingAction = UserAction.objects.filter(userID=curUser, time__gte=cutoffUserActionTime,place=newPlace)
	if existingAction:
		newAction = existingAction[0]
	else:
		newAction = UserAction.objects.create(userID=curUser, time = datetime.utcnow(), place = newPlace)
	
	if len(filterPlace)>0:
		#check to see if tag exists
		for placeTag in filterPlace:
			if (placeTag.tag.text in tags) and (placeTag.tag not in newAction.tags.all()):
				placeTag.freq += 1

				#update score
				timeNow = datetime.utcnow()
				timeDelta = timeNow - placeTag.lastUpdate
				placeTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
				placeTag.score += 50
				placeTag.lastUpdate = timeNow

				#take out hashtag from the list
				position = tags.index(placeTag.tag.text)
				tags.pop(position)

				newAction.tags.add(placeTag.tag)
				
				placeTag.save()

			
	#create a new review with remaining tags that didn't match
	for hashtag in tags: 
		newVenueReview = PlaceTag.objects.create(place=newPlace, tag = Hashtag.objects.get(text=hashtag), freq=1, lastUpdate=datetime.utcnow(), score = initialScore)
		
		#log new user action
		if newVenueReview.tag not in newAction.tags.all():
			newAction.tags.add(newVenueReview.tag)
		

		newVenueReview.save()
	
	#add a point to the user
	curUser.points += 1
	curUser.save()

	newAction.save()

	#get personalized hashtags:
	personalTags = request.POST.getlist('personalTag')
	
	tagText = ""
	
	for tag in personalTags:
		if tag != '':
			if "#" in tag:
				tag = tag.replace("#", "")

			if " " in tag:
				tag = tag.replace(" ", "")

			newTag = UserTag.objects.create(user=curUser, lastUpdate = datetime.utcnow(), place = newPlace, tag=tag, score = initialScore, freq = 1)
			newTag.save()


	"""		
		tagText += "#" + tag + "\n\r"
	if tagText != "":
	"""
	

	redirectURL = "/venue/" + request.POST["venueId"]

	return HttpResponseRedirect(redirectURL)
		
		
def add_user(request):
	context = { }
	return render(request, 'registration/add_user.html', context)
	
def add_user_add(request):
	try:
		newUser = User.objects.create(username=request.POST['uname'], email=request.POST['email'])
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

		if request.POST.get('next'):
			return HttpResponseRedirect(request.POST['next'])
		else:
			return HttpResponseRedirect('/')	
		
	
	except:
		error=1
		context = {'error':error}
		return render(request, 'registration/add_user.html', context)
	
	
	
@login_required()
def view_fav(request):
	##find today's date to find items close to it in db                                                                                                                                  
	date = datetime.utcnow()
	#for testing purposes, hardcode datetime                                                                                                                                             
	#date = datetime(2013, 12, 28, 22, 40, 41, 879000)                                                                                                                                   
	timeDeltaForCutoff = timedelta(hours=-2)
	cutoffTime = date + timeDeltaForCutoff
	curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
	userName = curUser.user.username
	
	favorites = curUser.favoritePlaces.all()
	
	favList = []
	
	for placeItem in favorites:
		url = 'https://api.foursquare.com/v2/venues/' + placeItem.placeID + '?client_id=T4XPWMEQAID11W0CSQLCP2P0NXGEUSDZRV4COSBJH2QEMC2O&client_secret=0P1EQQ3NH102D0R3GNGTG0ZAL0S5T41YDB2NPOOMRMO2I2EO&v=20130815'
		req = urlopen(url).read()
		place = json.loads(req).get("response").get("venue")
		
		"""
		oauth_request = oauth2.Request('GET', url, {})
		oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),'oauth_timestamp': oauth2.generate_timestamp(),'oauth_token': token, 'oauth_consumer_key': consumer_key})

		token = oauth2.Token(token, token_secret)
		oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
		signed_url = oauth_request.to_url()

		req = urlopen(signed_url).read()
		place = json.loads(req)
		"""
		
		
		#distance = round(place['location']['distance'] * 0.000621371192, -int(floor(log10(place['location']['distance'] * 0.000621371192))))
		category = place['categories'][0]['name']
		image_url = place['categories'][0]['icon']['prefix'] + '64' + place['categories'][0]['icon']['suffix']
		color=getColorTheme(placeItem.placeID)
		

		#grab top 5 hashtags
		hashtags = {}
		finalScore = 0.0
		allTagsForPlace = PlaceTag.objects.filter(place = placeItem, lastUpdate__gte = cutoffTime)
		for placeInstance in allTagsForPlace:
			hashtags[placeInstance.tag.text] = placeInstance.score
			finalScore + placeInstance.score

		orderHashtags = Counter(hashtags)
		topTags = orderHashtags.most_common(5)
		topHashtags = [i[0] for i in topTags]

		
		addToList = {'userName':userName, 'id' : placeItem.placeID, 'name' : placeItem.placeName, 'picture' : image_url, 'types' : category, 'finalScore' : finalScore, 'hashtags':topHashtags, 'color':color}
		
		favList.append(addToList)
	
	favList.sort(key=lambda x:x['finalScore'])
	
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
	

def view_profile(request, user_id):
	#get username, favorites list, last activity
	curUser = getUserProfile(user_id)
	userName = getUsername(user_id)
	
	"""
	#last places reviewed, in order of time 
	lastVisited = UserAction.objects.filter(userID=User.objects.get(id=request.user.id)).order_by('-time')
	
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
	"""

	favPlaceList = curUser.favoritePlaces
	context = {'userName':userName,'firstName': curUser.user.first_name, 'favorites':favPlaceList.all()}
	return render(request, 'places/view_profile.html', context)
	
def search(request):
	context = {}
	return render(request, 'places/search', context)
	
	
def map(request):
	context = {}
	return render(request, 'places/maps', context)

def feedback(request):
	context = {}
	return render(request, 'places/feedback.html', context)


def feedback_submit(request):
	#if signed in and if not signed in:
	if request.user.id:
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		new_feedback = UserFeedback.objects.create(feedback=request.POST['feedback'], date=datetime.today(), userID=curUser)

	else:
		new_feedback = UserFeedback.objects.create(feedback=request.POST['feedback'], date=datetime.today(), userID=UserProfile.objects.get(username='defaultFeedback'))
	
	new_feedback.save()

	return HttpResponseRedirect('/')

def about(request):
	context = {}
	return render(request, 'places/about.html', context)

def tag(request):
	#get username
	if request.user.is_authenticated():
		userName = getUsername(request.user.id)
	else:
		userName = ''

	##find today's date to find items close to it in db                                                                                                                                  
	date = datetime.utcnow()                                                                                                                              
	timeDeltaForCutoff = timedelta(hours=-2)
	cutoffTime = date + timeDeltaForCutoff


	if request.POST.get('position'):
		curLoc = request.POST['position']

	if request.POST.get('hashtag'): 
		hashtag = request.POST['hashtag']

	

	placetagsWithTag = PlaceTag.objects.filter(tag__text=hashtag, lastUpdate__gte = cutoffTime)
	placeTagList = []

	"""YELP API
	# Values for access
	consumer_key = 'nee5cvfcAEBHCg3wSGSdKw'
	consumer_secret = '3FmOuF9CLBGjyITGF66hbKmbgho'
	token = 'Ta-DBi45PaqkBhBnPJ1xpv1mmIjkVmxP'
	token_secret = 'ngCe85K7Xk6Sq37hI-4T-rE1Xtw'

	consumer = oauth2.Consumer(consumer_key, consumer_secret)
	"""


	for placeTag in placetagsWithTag:
		url = 'https://api.foursquare.com/v2/venues/' + placeTag.place.placeID + '?ll=' + curLoc + '&&client_id=T4XPWMEQAID11W0CSQLCP2P0NXGEUSDZRV4COSBJH2QEMC2O&client_secret=0P1EQQ3NH102D0R3GNGTG0ZAL0S5T41YDB2NPOOMRMO2I2EO&v=20130815'
		req = urlopen(url).read()
		place = json.loads(req).get("response").get("venue")
		
		"""
		oauth_request = oauth2.Request('GET', url, {})
		oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),'oauth_timestamp': oauth2.generate_timestamp(),'oauth_token': token, 'oauth_consumer_key': consumer_key})

		token = oauth2.Token(token, token_secret)
		oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
		signed_url = oauth_request.to_url()

		req = urlopen(signed_url).read()
		place = json.loads(req)
		"""
		
		
		distance = round(place['location']['distance'] * 0.000621371192, -int(floor(log10(place['location']['distance'] * 0.000621371192))))
		category = place['categories'][0]['name']
		image_url = place['categories'][0]['icon']['prefix'] + '64' + place['categories'][0]['icon']['suffix']
		color=getColorTheme(placeTag.place.placeID)
		finalScore = placeTag.score + 1 / distance

		#grab top 5 hashtags
		hashtags = {}
		allTagsForPlace = PlaceTag.objects.filter(place = placeTag.place, lastUpdate__gte = cutoffTime)
		for placeInstance in allTagsForPlace:
			hashtags[placeInstance.tag.text] = placeInstance.score

		orderHashtags = Counter(hashtags)
		topTags = orderHashtags.most_common(5)
		topHashtags = [i[0] for i in topTags]




		placeTagList.append({'id' : placeTag.place.placeID, 'name' : placeTag.place.placeName, 'picture' : image_url, 'types' : category, 'distance' : distance, 'finalScore' : finalScore, 'hashtags':topHashtags, 'color':color})
	

	placeTagList.sort(key=lambda x:x['finalScore'])

	#get all hashtags to display on header
	tags = Hashtag.objects.all()

	context = {'placeTagList' : placeTagList, 'hashtag':hashtag, 'headerUIAdditions':'hi', 'username':userName, 'tags':tags}
	return render(request, 'places/tag.html', context)



#####################################functions to call in views!#############################
def getColorTheme(id):
        ##find today's date to find items close to it in db                                                                                                                                  
        date = datetime.utcnow()
        #for testing purposes, hardcode datetime                                                                                                                                             
        #date = datetime(2013, 12, 28, 22, 40, 41, 879000)                                                                                                                                   
        timeDeltaForCutoff = timedelta(hours=-2)
        cutoffTime = date + timeDeltaForCutoff
	color = '127,127,127'
	if Place.objects.filter(placeID=id).exists():
		numRecentReviews = UserAction.objects.filter(place=Place.objects.get(placeID=id), time__gte = cutoffTime)

		color = '46,117,182'
		if len(numRecentReviews) >= 5:
			color = '255,80,80'
		elif len(numRecentReviews) >= 2:
			color = '128,0,128'
	return color

def isBlacklistedCategory(place):
	if place['categories'][0]['id'] in CategoryBlacklist:
		return True
	else:
		return False

def getUsername(uid):
	#curUser=UserProfile.objects.get(user=User.objects.get(id=uid))
	userName = (User.objects.get(id=uid)).username

	return userName

def getUserProfile(uid):
	curUser = UserProfile.objects.get(user=User.objects.get(id=uid))
	return curUser


############################################################################################
