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
from places.models import UserProfile, PlaceName, Hashtag, Place, UserAction, FavoritePlace
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
	curRev = Place.objects.filter(time__gte = cutoffTime)
	curRevList = list(set([i.placeId.placeId for i in curRev]))

	apiCall = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+curLoc+"&radius=550&types=bar|casino|night_club&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0"

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	places = json.loads(req).get("results")

	#for each place, do a check for id in curRevList, and append hashtag information
	#create two dictionaries to access for next view, one that have data for, one that we don't
	placeMatch = []
	placeNoMatch = []
	
	for place in places:
		temp = {}
		if place['reference'] in curRevList:
			#iterate over curRev and find all instances to append to dict to append to json
			hashtags = {}
			for i in curRev:
				if i.placeId.placeId == place['reference']:
					hashtags[i.tag.tag] = {'score' : i.score}
					
			#TO-DO: create order of list
					
			#check if price_level and rating exist and append
			if 'rating' not in place.keys():
				place['rating'] = 'NA'
			if 'price_level' not in place.keys():
				place['price_level'] = 'NA'
				
			temp = {'name': place['name'],'reference': place['reference'], 'rating':place['rating'], 'price_level':place['price_level'], 'types':place['types'], 'vicinity':place['vicinity'], 'hashtags':hashtags}
			
			#append
			placeMatch.append(temp)
		
		else:
			#check to see if price level and rating exist
			if 'rating' not in place.keys():
				place['rating'] = 'NA'
			if 'price_level' not in place.keys():
				place['price_level'] = 'NA'
				
			temp = {'name': place['name'], 'reference': place['reference'], 'rating':place['rating'], 'price_level':place['price_level'], 'types':place['types'], 'vicinity':place['vicinity']}
			
			#append
			placeNoMatch.append(temp)

	context = { 'placeMatch':placeMatch, 'placeNoMatch':placeNoMatch } #'examplePlaces':examplePlaces}
	return render(request, 'places/index.html', context)
	
	
def placeDetail(request,place_id):
	#make call to Google API for information
	apiCall = "https://maps.googleapis.com/maps/api/place/details/json?reference=" + place_id + "&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0"

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	place = json.loads(req).get("result")
	
	#get tags in our database
	tags = Place.objects.filter(placeId__placeId = place['id'], time__gte = cutoffTime)
	
	#send relevant information to templates
	#check to see if all keys exist. If not, assign 'NA' values
	if 'formatted_phone_number' not in place.keys():
		place['formatted_phone_number'] = 'NA'
		
	if 'formatted_address' not in place.keys():
		place['formatted_address'] = 'NA'
	
	if 'rating' not in place.keys():
		place['rating'] = 'NA'
	
	if 'price_level' not in place.keys():
		place['price_level'] = 'NA'
		
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
	
def submitReview(request):
	#grab all hashtags to display
	tags = Hashtag.objects.all()
	
	context = {'tags':tags}
	return render(request, 'places/submitReview.html', context)
	
def submitReviewVenue(request, place_name, reference):
	#grab all hashtags to display
	tags = Hashtag.objects.all()
	
	context = {'tags':tags, 'id':reference, 'name':place_name}
	return render(request, 'places/submitReviewVenue.html', context)
	
def submit_submitReviewVenue(request):
	#Check if place exists. If not, add place
	if PlaceName.objects.get(id=request.POST['id']).exists():
		newPlace = PlaceName.objects.get(id=request.Post['id'])
	else:
		newPlace = PlaceName.objects.create(placeId = request.POST['id'], venueName=request.POST['name'])
	
	#get list of tags
	#listTags = request.body
	tags=[]
	for tag in request.POST:
		tags.append(tag)

	#Filter for all instances of Places with same placeId and tag
	filterPlace = Place.objects.filter(placeId=newPlace, time__gte = cutoffTime)
	
	if len(filterPlace)>0:
		#check to see if tag exists
		for reviews in filterPlace:
			if tag__tag in tags:
				reviews.freq++
				#update score
				tags.del(tag__tag)
			reviews.save()
			
		#create a new review with remaining tags that didn't match
		for hashtag in tags: 
			newVenueReview = Place.objects.create(placeId=newPlace, tag = Hashtag.objects.get(tag=hashtag), freq=1, time=datetime.today(), score = 100)
			fix score
			
			#update UserAction and UserProfile Points
			
			newVenueReview.save()
			
	return HttpResponseRedirect('/')

def submit_submitReview(request):
	
	return HttpResponseRedirect('/')
		
def fav(request):
	context = {}
	return render(request, 'places/fav', context)
		
		
def view_profile(request):
	context = {}
	return render(request, 'places/view_profile', context)
	
def search(request):
	context = {}
	return render(request, 'places/search', context)