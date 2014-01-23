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

#import googlemaps

##find today's date to find items close to it in db
#today = datetime.today()
#for testing purposes, hardcode datetime
date = datetime(2013, 12, 28, 22, 40, 41, 879000)
cutoffTime = datetime(date.year,date.month,date.day, date.hour-2, date.minute, date.second, date.microsecond)

# home/index page. 
def index(request):
	#find curLong + curLat
	#HOW DO YOU DO THIS? Hard code for now
	curLoc = '37.798542,-122.422345'
			
	
	

	#grab array of reviews from our models
	curRev = PlaceTag.objects.filter(lastUpdate__gte = cutoffTime)
	curRevList = list(set([placeTag.place.placeID for placeTag in curRev]))

	apiCall = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+curLoc+"&radius=550&types=bar|casino|night_club&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0"

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	venues = json.loads(req).get("results")

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
					hashtags[placeTag.tag.text] = placeTag.score
					
			#TO-DO: create order of list
					
			#check if price_level and rating exist and append
			if 'rating' not in place.keys():
				place['rating'] = 'N/A'
			if 'price_level' not in place.keys():
				place['price_level'] = 'N/A'
				
			temp = {'name': place['name'], 'id': place['id'], 'reference':place['reference'], 'rating': place['rating'], 'price_level': place['price_level'], 'types': place['types'], 'vicinity': place['vicinity'], 'hashtags': hashtags}
			
			#append
			placeMatch.append(temp)
		
		else:
			#check to see if price level and rating exist
			if 'rating' not in place.keys():
				place['rating'] = 'N/A'
			if 'price_level' not in place.keys():
				place['price_level'] = 'N/A'
				
			temp = {'name': place['name'], 'id': place['id'], 'reference':place['reference'], 'rating':place['rating'], 'price_level':place['price_level'], 'types':place['types'], 'vicinity':place['vicinity']}
			
			#append
			placeNoMatch.append(temp)

	context = { 'placeMatch': placeMatch, 'placeNoMatch': placeNoMatch }
	return render(request, 'places/index.html', context)
	
	
def placeDetail(request,place_id):
	#make call to Google API for information
	apiCall = "https://maps.googleapis.com/maps/api/place/details/json?reference=" + place_id + "&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0"

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	place = json.loads(req).get("result")
	
	#get PlaceTags in our database
	tags = PlaceTag.objects.filter(place__placeID= place['id'], lastUpdate__gte = cutoffTime)
	
	#send relevant information to templates
	#check to see if all keys exist. If not, assign 'NA' values
	if 'formatted_phone_number' not in place.keys():
		place['formatted_phone_number'] = 'N/A'
		
	if 'formatted_address' not in place.keys():
		place['formatted_address'] = 'N/A'
	
	if 'rating' not in place.keys():
		place['rating'] = 'N/A'
	
	if 'price_level' not in place.keys():
		place['price_level'] = 'N/A'
		
	#create address
	address = []
	address.append(place['address_components'][0]['long_name'] + ' ' + place['address_components'][1]['long_name'])
	address.append(place['address_components'][2]['long_name'] + ',' + place['address_components'][3]['long_name'])
	
	#see if have info on opening times
	try: place['open'] = place['opening_hours']['open_now']
	except: place['open'] = ''
	
	#find what the most descriptive hashtags have been in the past?
	
	
	context = {'id':place['id'], 'tags':tags, 'name':place['name'], 'open': place['open'], 'venueTypes':place['types'], 'address':address, 'phone': place['formatted_phone_number'], 'price':place["price_level"], 'rating':place['rating'], 'photos':place}
	
	return render(request, 'places/placeDetail.html', context)

#later, we will merge submitReview and submitReviewVenue to one view. It's a simple if statement to fix in a template file	
@login_required()
def submitReview(request):
	#grab all hashtags to display
	tags = Hashtag.objects.all()
	
	context = {'tags':tags}
	return render(request, 'places/submitReview.html', context)

@login_required()
def submitReviewVenue(request, place_name, reference):
	#grab all hashtags to display
	tags = Hashtag.objects.all()
	
	context = {'tags':tags, 'id':reference, 'name':place_name}
	return render(request, 'places/submitReviewVenue.html', context)

	
def submit_submitReview(request):
	#Check if place exists. If not, add place
	if Place.objects.filter(placeID=request.POST['venueId']).exists():
		newPlace = Place.objects.get(placeID=request.POST['venueId'])
	else:
		newPlace = Place.objects.create(placeID = request.POST['venueId'], placeName=request.POST['venueName'])
		newPlace.save()
	
	#get list of tags
	#listTags = request.body
	tags= request.POST.getlist('tagNames')
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
		for reviews in filterPlace:
			if reviews.tag.text in tags:
				reviews.freq +=1
				#update score
				
				#take out hashtag from the list
				position = tags.index(reviews.tag.text)
				tags.pop(position)
			reviews.save()
			
	#create a new review with remaining tags that didn't match
	for hashtag in tags: 
		newVenueReview = PlaceTag.objects.create(place=newPlace, tag = Hashtag.objects.get(text=hashtag), freq=1, lastUpdate=datetime.today(), score = 100)
		
		#fix score
		
		#update UserAction and UserProfile Points
		
		newVenueReview.save()
	
			
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
	favorites = curUser.favoritePlaces.all()
	
	favList = []
	
	for venue in favorites:
		hashtags = {}
		temp = PlaceTag.objects.filter(place=venue, lastUpdate__gte=cutoffTime)
		
		for i in temp:
			hashtags[i.tag.text]=i.score
	
		#create dictionsary to append to list
		addToList = {'name':venue.placeName , 'hashtags':hashtags}
		
		favList.append(addToList)
	
	
	
	context = {'favorites':favList, 'user':curUser.user.username}
	
	return render(request, 'places/view_fav.html', context)
		
@login_required()
def add_fav(request, placeId):
	curUser=UserProfile.objects.get(user=User.objects.get(id=request.user.id))
	current_venue = Place.objects.get(placeID = placeId)

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
	
	context = {'firstName': curUser.user.first_name, 'favorites':placeList}
	return render(request, 'places/view_profile.html', context)
	
def search(request):
	context = {}
	return render(request, 'places/search', context)