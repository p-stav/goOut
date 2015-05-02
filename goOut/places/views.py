from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from urllib import urlopen
import json, pprint
from datetime import datetime, timedelta
from places.models import UserProfile, Place, Hashtag, PlaceTag, UserAction, UserFeedback, UserTag, HashtagCategory, JoinBeta
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

maxFontSizePercentage = 167
minFontSizePercentage = 50

CategoryBlacklist = ['4bf58dd8d48988d1e0931735',
'4bf58dd8d48988d1d5941735', '4bf58dd8d48988d103941735']

############### home view ##########
def homeView(request):
	context = {}
	return render(request, 'places/kefiLabs.html')


############### kefi ###############
def kefiHomeView(request):
	context = {}
	return render(request, 'places/home.html', context)

def getKefi(request):
	context = {}

	return render(request, 'places/getkefi.html', context)

def getKefi_submit(request):
	newBeta = JoinBeta.objects.create(name=request.POST['name'], email=request.POST['email'], date=datetime.today(),  note=request.POST['note'])
	newBeta.save()

	return render(request, 'places/getkefi.html')

def aboutUs(request):
	context = {}
	return render(request, 'places/aboutUs.html', context)



############### assassins getkefi.com  view ###############
def assassins(request):
	context = {}
	return render(request, 'places/assassins.html', context)

def assassins_terms(request):
	context = {}
	return render(request, 'places/assassins_terms.html', context)

def assassins_privacy(request):
	context = {}
	return render(request, 'places/assassins_privacy.html', context)


############### ripple getkefi.com  view ###############
def ripple(request):
	context = {}
	return render(request, 'places/ripple.html', context)

def ripple_terms(request):
	context = {}
	return render(request, 'places/ripple_terms.html', context)

def ripple_privacy(request):
	context = {}
	return render(request, 'places/ripple_privacy.html', context)

def ripple_ambassador(request):
	context = {}
	return render(request, 'places/ripple_ambassador.html', context)

def ripple_careers(request):
	context = {}
	return render(request, 'places/ripple_careers.html', context)




##########################################################
######Kefi v 0 ###########################################
##########################################################

def redirectIOS(request):
	context = {}

	#foursquare data for api call
	client_id = 'T4XPWMEQAID11W0CSQLCP2P0NXGEUSDZRV4COSBJH2QEMC2O'
	client_secret = '0P1EQQ3NH102D0R3GNGTG0ZAL0S5T41YDB2NPOOMRMO2I2EO'
	category_id =  '4bf58dd8d48988d116941735,50327c8591d4c4b30a586d5d,4bf58dd8d48988d11e941735,4bf58dd8d48988d118941735,4bf58dd8d48988d1d8941735,4bf58dd8d48988d120941735,4bf58dd8d48988d121941735,4bf58dd8d48988d11f941735,4bf58dd8d48988d11b941735,4bf58dd8d48988d1d4941735,4bf58dd8d48988d11d941735,4bf58dd8d48988d122941735,4bf58dd8d48988d123941735'
	redirectURI = 'http://www.getkefi.com/redirectIOS'

	if(request.GET.get('code')):
		code = request.GET['code']

		url = "https://foursquare.com/oauth2/access_token?client_id=" + client_id + "&client_secret=" + client_secret + "&grant_type=authorization_code&redirect_uri="+ redirectURI + "&code=" + code

		#make request and receive json
		req = urlopen(url).read()
		access_token = json.loads(req).get("access_token")

		context = {'access_token':access_token, "code":code}

	return render(request, 'places/redirectIOS.html', context)

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
	#find today's date to find items close to it in db                                                                                                                                  
	cutoffTime = getCutoffTime()

	#get username
	if request.user.is_authenticated():
		curUser = getUserProfile(request.user.id)
		userName = getUsername(curUser)
	else:
		userName = ''
	
	#get curLong + curLat, or redirect to get info
	if request.POST.get('position'):
		curLoc = request.POST['position']
	else: return HttpResponseRedirect('/v0')


	if curLoc == '': #hardcode if fails.
		curLoc = '47.6159392,-122.3268701' #Seattle Pine/Bellevue
		#SF chestnut/VanNess.798542,-122.422345'

	#foursquare data for api call
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



	"""
	GOOGLE PLACES API:

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
		if 'address' in place['location'].keys():
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
				
				image_url = place['categories'][0]['icon']['prefix'] + 'bg_64' + place['categories'][0]['icon']['suffix']

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
				topTags = orderHashtags.most_common(4)
				topHashtags = [i[0] for i in topTags]
				
				#round distance, list of categories, and location
				distance = round(place['location']['distance'] * 0.000621371192, -int(floor(log10(place['location']['distance'] * 0.000621371192))))
				category = place['categories'][0]['name']
				
				image_url = place['categories'][0]['icon']['prefix'] + 'bg_64' + place['categories'][0]['icon']['suffix']


					
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
				
				image_url = place['categories'][0]['icon']['prefix'] + 'bg_64' + place['categories'][0]['icon']['suffix']

				temp = {'picture': image_url, 'name': place['name'], 'id': place['id'], 'types': category, 'distance':distance, 'color':'127,127,127'}
				
				#append
				placeNoMatch.append(temp)

	#get all hashtags to display
	tags = groupTags()


	sortMethod = ''
	context = {'tags':tags, 'sort':sortMethod, 'url':url, 'search':term, 'userName':userName, 'placeMatch': placeMatch, 'placeMatchOld':placeMatchOld, 'placeNoMatch': placeNoMatch, 'headerUIAdditions':'hi' }


	return render(request, 'places/index.html', context)
	
	
def placeDetail(request,place_id):
	##find today's date to find items close to it in db                                                                                                                                  
	cutoffTime  = getCutoffTime()
	
	#booleans for favorited and curUser for which tags submitted
	placeFavorited = False
	curUser = False

	#get username
	if request.user.is_authenticated():
		curUser = getUserProfile(request.user.id)
		userName = getUsername(curUser)
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
	"""
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

	

	"""
	apiCall = "https://maps.googleapis.com/maps/api/place/details/json?reference=" + place_id + "&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0"

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	place = json.loads(req).get("result")
	"""
	#####get PlaceTags and UserTags in our database
	if len(PlaceTag.objects.filter(place__placeID= place['id'], lastUpdate__gte = cutoffTime)) or len(UserTag.objects.filter(place__placeID=place['id'], lastUpdate__gte = cutoffTime)) >0:
		placeTags = PlaceTag.objects.filter(place__placeID = place['id'], lastUpdate__gte = cutoffTime).order_by('-score')
		userTags = UserTag.objects.filter(place__placeID = place['id'], lastUpdate__gte = cutoffTime).order_by('-score')
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
		
		placeTags=[]
		userTags=[]

	#send relevant information to templates
	#check to see if all keys exist. If not, assign 'NA' values

	#Place userTags and tags data in same lists. Define fontSizes and frequenceis
	allTags = []

	for Tag in placeTags:
		tagObject = {}
		tagObject["tagText"] = Tag.tag.text
		tagObject["freq"] = Tag.freq
		tagObject["score"] = Tag.score
		tagObject["lastUpdate"] = Tag.lastUpdate
		
		checkTag = Hashtag.objects.get(text=tagObject["tagText"])
		tagObject["wasTagged"] = checkTag.useractionHashtag_set.filter(userID = curUser, place__placeID = place['id'], time__gte = cutoffTime).exists()

		allTags.append(tagObject)

	for Tag in userTags:
		tagObject = {}
		tagObject["tagText"] = Tag.tag
		tagObject["freq"] = Tag.freq
		tagObject["score"] = Tag.score
		tagObject["lastUpdate"] = Tag.lastUpdate
		tagObject["username"] = Tag.userID.user.username
		
		
		tagObject["wasTagged"] = False

		if UserTag.objects.filter(tag=tagObject["tagText"], place__placeID=place['id']).exists():
			checkTag = UserTag.objects.get(tag=tagObject["tagText"], place__placeID=place['id'])
			tagObject["wasTagged"] =checkTag.useractionUserTag_set.filter(userID = curUser, place__placeID = place['id'], time__gte = cutoffTime).exists()
		

		allTags.append(tagObject)
		

	#sort allTags in order of score
	allTags.sort(key=lambda x:x['score'])

	#define lists to zip together
	tagText = []
	fontSizes = []
	tagsFreq = []
	username = []
	wasTagged = []

	#update scores
	timeNow = datetime.utcnow()
	for placeTag in allTags:
		if placeTag["freq"] > 0:
			timeDelta = timeNow - placeTag["lastUpdate"]
			placeTag["score"] *= exp(-1 * timeDecayExponent * timeDelta.total_seconds())
			placeTag["lastUpdate"] = timeNow

			if "username" not in placeTag.keys():
				placeTag["username"] = "Kefi"
			#placeTag.save()

			tagText.append(placeTag["tagText"])

			fontSizePercentage = (placeTag["score"] / highestScore) * (maxFontPercentage - minFontPercentage) + minFontPercentage
			
			if maxFontSizePercentage < fontSizePercentage or minFontSizePercentage > fontSizePercentage:
				fontSizePercentage = checkFontSizePercentage(fontSizePercentage)
			

			fontSizes.append(fontSizePercentage)
		
			tagsFreq.append(placeTag["freq"])

			username.append(placeTag["username"])

			wasTagged.append(placeTag["wasTagged"])

	'''#calculate + grab font sizes, freq and tags
	totalScore = 0.0
	for placeTag in allTags:
	'''	
	
		

		

	tagsWithFonts = zip(tagText, fontSizes, tagsFreq, username, wasTagged)
	tagsWithFonts.reverse()

	address  = []

	if 'address' in place['location'].keys():
		address.append(place['location']['address'])
	if 'crossStreet' in place['location'].keys():
		address.append(place['location']['crossStreet'])
	category = category = place['categories'][0]['name']

	image_url = place['categories'][0]['icon']['prefix'] + 'bg_64' + place['categories'][0]['icon']['suffix']

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
	tags = groupTags()

	context = {'userName':userName, 'id':place['id'], 'oldTags':oldTags, 'tagsWithFonts':tagsWithFonts, 'name':place['name'], 'venueTypes':category, 'address':address, 'placeFavorited':placeFavorited, 'color':color, 'picture' : image_url, 'tags':tags}
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
	tags = groupTags()
	
	context = {'userName':userName,'tags':tags}
	return render(request, 'places/submitReview.html', context)

def submitReviewVenue(request, place_name, reference):
	#get username
	if request.user.is_authenticated():
		curUser = UserProfile.objects.get(user=User.objects.get(id=request.user.id))
		userName = curUser.user.username
	else:
		userName = False
	
	#get color theme
	color=getColorTheme(reference)

	#grab all hashtags to display
	tags = groupTags()
	
	context = {'userName':userName, 'tags':tags, 'id':reference, 'name':place_name, 'color':color}
	return render(request, 'places/submitReviewVenue.html', context)

	
def submit_submitReview(request):
	##find today's date to find items close to it in db                                                                                                                                  
	cutoffTime = getCutoffTime()
	
	curUser = getUserProfile(request.user.id)
	

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
	if curUser !=False:
		newAction = checkExistingAction(curUser, newPlace)
	
	#get list of tags
	#listTags = request.body
	if len(request.POST.getlist('tagNames'))>0:
		tags = request.POST.getlist('tagNames')

		#Filter for all instances of Places with same placeId and tag within alotted time
		filterPlace = PlaceTag.objects.filter(place=newPlace)
		
		
		if len(filterPlace)>0:
			#check to see if tag exists
			for placeTag in filterPlace:
				if (placeTag.tag.text in tags): #and (placeTag.tag not in newAction.tags.all()):

					#update score
					timeNow = datetime.utcnow()
					timeDelta = timeNow - placeTag.lastUpdate
					placeTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
					placeTag.score += 50

					#update freq and lastUpdate
					if timeDelta.total_seconds() > 7200:
						placeTag.freq = 1
					else:
						placeTag.freq += 1

					placeTag.lastUpdate = timeNow

					#take out hashtag from the list
					position = tags.index(placeTag.tag.text)
					tags.pop(position)

					if curUser!=False:
						newAction.tags.add(placeTag.tag)
					
					placeTag.save()

				elif (placeTag.tag.text in tags):
					position = tags.index(placeTag.tag.text)
					tags.pop(position)

		#create a new review with remaining tags that didn't match
		for hashtag in tags: 
			newVenueReview = PlaceTag.objects.create(place=newPlace, tag = Hashtag.objects.get(text=hashtag), freq=1, lastUpdate=datetime.utcnow(), score = initialScore)
			
			#log new user action
			if curUser !=False:
				if newVenueReview.tag not in newAction.tags.all():
					newAction.tags.add(newVenueReview.tag)
					newAction.save()
			

			newVenueReview.save()
		

	###################get personalized hashtags:##########################
	if curUser != False and len(request.POST.getlist('personalTag')) > 0:
		personalTags = request.POST.getlist('personalTag')
		lowerPersonalTags = [i.lower() for i in personalTags]
		
		#grab all UserTags associated with place to see if this one exists
		existingUserTag = UserTag.objects.filter(place = newPlace)

		#does userTag exist? 
		#make all strings lower to catch all capitlaization instances
		userActionPersonalTags = newAction.userTags.all()
		lowerUserActionPersonalTags = [i.tag.lower() for i in userActionPersonalTags]

		if len(personalTags)>0:
			for userTag in existingUserTag:
				#if existing tag not in a user action of curUser, and that existing tag was submitted by user:
				if (userTag.tag.lower() not in lowerUserActionPersonalTags) and (userTag.tag.lower() in lowerPersonalTags):
					
					#update score
					timeNow = datetime.utcnow()
					timeDelta = timeNow - userTag.lastUpdate
					userTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
					userTag.score += 50

					#update freq and lastUpdate
					if timeDelta.total_seconds() > 7200:
						userTag.freq = 1
					else:
						userTag.freq += 1

					userTag.lastUpdate = timeNow

					#take out hashtag from the list
					position = lowerPersonalTags.index(userTag.tag.lower())
					personalTags.pop(position)

					newAction.userTags.add(userTag)
					
					userTag.save()

				#If this tag is in an existing userAction, meaning you can't submit a like:
				elif (userTag.tag.lower() in lowerPersonalTags):
						position = lowerPersonalTags.index(userTag.tag)
						personalTags.pop(position)	

			#create new object for userTag
			for hashtag in personalTags: 
				if hashtag != '':
					if "#" in hashtag:
						hashtag = hashtag.replace("#", "")

					if " " in hashtag:
						hashtag = hashtag.replace(" ", "")

					newVenueReview = UserTag.objects.create(userID = curUser, place=newPlace, tag = hashtag, freq=1, lastUpdate=datetime.utcnow(), score = initialScore)
					newVenueReview.save()
					
					#log new user action
					if newVenueReview.tag not in newAction.userTags.all():
						newAction.userTags.add(newVenueReview)

						newAction.save()


		
	#add a point to the user
	if curUser!=False:
		curUser.points += 1
		curUser.save()

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
		image_url = place['categories'][0]['icon']['prefix'] + 'bg_64' + place['categories'][0]['icon']['suffix']
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
		curUser = getUserProfile(request.user.id)
		userName = getUsername(curUser)
	else:
		userName = ''

	##find today's date to find items close to it in db                                                                                                                                  
	cutoffTime = getCutoffTime()

	if request.POST.get('position'):
		curLoc = request.POST['position']

	if request.POST.get('hashtag'): 
		hashtag = request.POST['hashtag']

	

	placetagsWithTag = PlaceTag.objects.filter(tag__text=hashtag, lastUpdate__gte = cutoffTime)
	placeMatch = []

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
		image_url = place['categories'][0]['icon']['prefix'] + 'bg_64' + place['categories'][0]['icon']['suffix']
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




		placeMatch.append({'id' : placeTag.place.placeID, 'name' : placeTag.place.placeName, 'picture' : image_url, 'types' : category, 'distance' : distance, 'finalScore' : finalScore, 'hashtags':topHashtags, 'color':color})
	

	placeMatch.sort(key=lambda x:x['finalScore'])

	#get all hashtags to display on header
	tags = groupTags()

	context = {'placeMatch' : placeMatch, 'hashtag':hashtag, 'headerUIAdditions':'hi', 'username':userName, 'tags':tags}
	return render(request, 'places/tag.html', context)


def placeTagUpdate(request):
	if request.is_ajax():
		tagText = request.GET.get('tagText')
		hashtag = Hashtag.objects.get(text = tagText)

		place = request.GET.get('place')

		#get User and cutoffTime
		curUser = getUserProfile(request.user.id)
		cutoffTime = getCutoffTime()
	

		if (tagText is not None) and (place is not None):
			placeTag = PlaceTag.objects.get(place__placeID = place, tag__text = tagText)

			#if user took this action, then we subtract
			if (hashtag.useractionHashtag_set.filter(userID = curUser, place__placeID = place, time__gte = cutoffTime).exists()):
			
				#remove instance from user action
				userAction = hashtag.useractionHashtag_set.filter(userID = curUser, place__placeID = place, time__gte = cutoffTime)[0]

				userAction.tags.remove(hashtag)
				userAction.save()

				#grab necessary information to undo score
				#update score
				fontSizePercentage = 0
				wasTagged = False
				freq = 0

				if placeTag.freq > 0:
						
					#update score
					timeNow = datetime.utcnow()
					timeDelta = timeNow - placeTag.lastUpdate
					placeTag.score /= exp(-timeDecayExponent * timeDelta.total_seconds())
					placeTag.score -= 50

					#update freq and lastUpdate
					if timeDelta.total_seconds() > 7200:
						placeTag.freq = 1
					else:
						placeTag.freq -= 1

					placeTag.lastUpdate = timeNow

					placeTag.save()

					#generate html for tagNode. Need font size as well
					fontSizePercentage = (placeTag.score / highestScore) * (maxFontPercentage - minFontPercentage) + minFontPercentage
					if maxFontSizePercentage < fontSizePercentage or minFontSizePercentage > fontSizePercentage:
						fontSizePercentage = checkFontSizePercentage(fontSizePercentage)

			else:
		
				#create user action for user if one does not exist
				placeObject = Place.objects.get(placeID = place)
				userAction = checkExistingAction(curUser, placeObject)

				
				userAction.tags.add(hashtag)

				#update score
				placeTag.freq += 1

				timeNow = datetime.utcnow()
				timeDelta = timeNow - placeTag.lastUpdate
				placeTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
				placeTag.score += 50
				placeTag.lastUpdate = timeNow

				placeTag.save()

				#gnerate html for tagNode. Need font size as well

				fontSizePercentage = (placeTag.score / highestScore) * (maxFontPercentage - minFontPercentage) + minFontPercentage
				if maxFontSizePercentage < fontSizePercentage or minFontSizePercentage > fontSizePercentage:
					fontSizePercentage = checkFontSizePercentage(fontSizePercentage)

				wasTagged = True

			userAction.save()
			#check if 
			data = {"tag": tagText, "freq":placeTag.freq, "username":"Kefi", "fontSize":fontSizePercentage, "wasTagged":wasTagged}

			return render_to_response("places/tagNode.html", data, context_instance=RequestContext(request))


def userTagUpdate(request):
	if request.is_ajax():
		tagText = request.GET.get('tagText')
		

		place = request.GET.get('place')

		#get User and cutoffTime
		curUser=UserProfile.objects.get(user=User.objects.get(id=request.user.id))		
		cutoffTime = getCutoffTime()
	

		if tagText is not None and place is not None:
			userTag = UserTag.objects.get(place__placeID = place, tag = tagText)

			#if user took this action, then we subtract
			if (userTag.useractionUserTag_set.filter(userID = curUser, place__placeID = place, time__gte = cutoffTime).exists()):
				
				#remove instance from user action
				userAction = userTag.useractionUserTag_set.filter(userID = curUser, place__placeID = place, time__gte = cutoffTime)[0]

				userAction.userTags.remove(userTag)
				userAction.save()

				
				#update score
				timeNow = datetime.utcnow()
				timeDelta = timeNow - userTag.lastUpdate
				userTag.score /= exp(-timeDecayExponent * timeDelta.total_seconds())
				userTag.score -= 50

				#update freq and lastUpdate
				if timeDelta.total_seconds() > 7200:
					userTag.freq = 1
				else:
					userTag.freq -= 1

				userTag.lastUpdate = timeNow

				userTag.save()

				#gnerate html for tagNode. Need font size as well

				fontSizePercentage = (userTag.score / highestScore) * (maxFontPercentage - minFontPercentage) + minFontPercentage
				if maxFontSizePercentage < fontSizePercentage or minFontSizePercentage > fontSizePercentage:
					fontSizePercentage = checkFontSizePercentage(fontSizePercentage)
				
				wasTagged = False

			else:
				#create user action for user if one does not exist
				placeObject = Place.objects.get(placeID = place)
				userAction = checkExistingAction(curUser, placeObject)

				userAction.userTags.add(userTag)
				
				#update score
				timeNow = datetime.utcnow()
				timeDelta = timeNow - userTag.lastUpdate
				userTag.score *= exp(-timeDecayExponent * timeDelta.total_seconds())
				userTag.score += 50

				#update freq and lastUpdate
				if timeDelta.total_seconds() > 7200:
					userTag.freq = 1
				else:
					userTag.freq += 1

				userTag.lastUpdate = timeNow

				userTag.save()

				#gnerate html for tagNode. Need font size as well

				fontSizePercentage = (userTag.score / highestScore) * (maxFontPercentage - minFontPercentage) + minFontPercentage
				if maxFontSizePercentage < fontSizePercentage or minFontSizePercentage > fontSizePercentage:
					fontSizePercentage = checkFontSizePercentage(fontSizePercentage)

				wasTagged = True

			userAction.save()
			data = {"tag": tagText, "freq":userTag.freq, "username": userTag.userID.user.username, "fontSize":fontSizePercentage, "wasTagged":wasTagged}

			return render_to_response("places/tagNode.html", data, context_instance=RequestContext(request))		

#####################################functions to call in views!#############################
def getColorTheme(id):
	cutoffTime = getCutoffTime()
	color = '255,255,255'
	
	if Place.objects.filter(placeID=id).exists():
		numRecentReviews = UserAction.objects.filter(place=Place.objects.get(placeID=id), time__gte = cutoffTime)

		colorBase = "46,117,182"
		color =  colorBase + ",0.1"
		if len(numRecentReviews) >= 5:
			color = colorBase +", 0.4"
		elif len(numRecentReviews) >= 2:
			color = colorBase + ",0.25"
	return color

def getCutoffTime():
	 ##find today's date to find items close to it in db                                                                                                                                  
	date = datetime.utcnow()
	#for testing purposes, hardcode datetime                                                                                                                                             
	#date = datetime(2013, 12, 28, 22, 40, 41, 879000)                                                                                                                                   
	timeDeltaForCutoff = timedelta(hours=-2)
	cutoffTime = date + timeDeltaForCutoff

	return cutoffTime

def isBlacklistedCategory(place):
	if place['categories'][0]['id'] in CategoryBlacklist:
		return True
	else:
		return False

def getUsername(uid):
	if uid==False:
		userName=False
	else:
		if UserProfile.objects.filter(user=User.objects.get(id=uid.user.id)).exists():
			userName = UserProfile.objects.get(user=User.objects.get(id=uid.user.id)).user.username
		else:
			userName = ""

	return userName

def getUserProfile(uid):
	try: curUser = UserProfile.objects.get(user=User.objects.get(id=uid))
	except: curUser = False
	
	return curUser


def checkExistingAction(curUser, newPlace):
	# check if existing UserAction otherwise add new one
	#for testing purposes, hardcode datetime                                                                                                                                             
	#date = datetime(2013, 12, 28, 22, 40, 41, 879000)                                                                                                                                   
	date = datetime.utcnow()
	timeDeltaForUserActionCutoff = timedelta(minutes=-5)
	cutoffUserActionTime = date + timeDeltaForUserActionCutoff
	existingAction = UserAction.objects.filter(userID=curUser, time__gte=cutoffUserActionTime, place = newPlace)
	
	if existingAction:
		newAction = existingAction[0]
	else:
		newAction = UserAction.objects.create(userID=curUser, time = datetime.utcnow(), place =  newPlace)
	newAction.save()

	return newAction

def checkFontSizePercentage(fontSizePercentage):
	if fontSizePercentage > maxFontSizePercentage:
		fontSizePercentage = maxFontSizePercentage
	if fontSizePercentage < minFontSizePercentage:
		fontSizePercentage = minFontSizePercentage

	return fontSizePercentage



def groupTags():
	#grab all categories
	categories = HashtagCategory.objects.all()

	#create dictionary with all categories and tags
	tags = []

	for category in categories:
		temp = []
		
		hashtags = Hashtag.objects.filter(category=category)
		temp = [i.text for i in hashtags ]
		tags.append([category.name, temp])

	return tags

############################################################################################