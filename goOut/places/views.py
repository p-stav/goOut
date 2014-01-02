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
		
	#find what the most descriptive hashtags have been in the past?
	
	context = {'tags':tags, 'name':place['name'], 'address':place['formatted_address'], 'phone': place['formatted_phone_number'], 'price':place["price_level"], 'rating':place['rating'], 'photos':place}
	
	return render(request, 'places/placeDetail.html', context)
	
def submitReview(request):

	context = {}
	return render(request, 'places/submitReview.html', context)