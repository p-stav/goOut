from django.shortcuts import render
from urllib import urlopen
import json, pprint
from datetime import datetime
from places.models import UserProfile, PlaceName, Hashtag, Place, UserAction, FavoritePlace
import sets

#import googlemaps

# home/index page. 
def index(request):
	#find curLong + curLat
	#HOW DO YOU DO THIS? Hard code for now
	curLoc = '37.798542,-122.422345'
			
	##find today's date to find items close to it in db
	#today = datetime.today()
	#for testing purposes, hardcode datetime
	date = datetime(2013, 12, 28, 22, 40, 41, 879000)

	#grab array of reviews from our models
	cutoffTime = datetime(date.year,date.month,date.day, date.hour-2, date.minute, date.second, date.microsecond)
	curRev = Place.objects.filter(time__gte = cutoffTime)
	curRevList = list(set([i.placeId.placeId for i in curRev]))

	apiCall = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+curLoc+"&radius=550&types=bar|casino|night_club&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0";

	#grab json object from google Places API
	req = urlopen(apiCall).read()
	places = json.loads(req).get("results")

	#for each place, do a check for id in curRevList, and append hashtag information
	#create two dictionaries to access for next view, one that have data for, one that we don't
	placeMatch = []
	placeNoMatch = []
	
	for place in places:
		temp = {}
		if place['id'] in curRevList:
			#iterate over curRev and find all instances to append to dict to append to json
			hashtags = {}
			for i in curRev:
				if i.placeId.placeId == place['id']:
					hashtags[i.tag.tag] = {'score' : i.score}
					
			#TO-DO: create order of list
					
			#try/except statements because json objects don't always have 'ratings' and 'price_level'. Append to lists. 
			#how do you use .exists() function?
			try: temp = {'name': place['name'],'id': place['id'], 'rating':place['rating'], 'price_level':place['price_level'], 'types':place['types'], 'vicinity':place['vicinity'], 'hashtags':hashtags}
			except: 
				try:temp = {'name': place['name'], 'id': place['id'], 'rating':'NA', 'price_level':place['price_level'], 'types':place['types'], 'vicinity':place['vicinity'], 'hashtags':hashtags}
				except:
					try: temp = {'name': place['name'], 'id': place['id'], 'rating':place['rating'], 'price_level':-1, 'types':place['types'], 'vicinity':place['vicinity'], 'hashtags':hashtags}
					except: temp = {'name': place['name'], 'id': place['id'], 'rating':'NA', 'price_level':-1 , 'types':place['types'], 'vicinity':place['vicinity'], 'hashtags':hashtags}
			#append
			placeMatch.append(temp)
		
		else:
			#nested try and excepts because json objects don't always have 'ratings' and 'price_level'
			try: temp = {'name': place['name'], 'id': place['id'], 'rating':place['rating'], 'price_level':place['price_level'], 'types':place['types'], 'vicinity':place['vicinity']}
			except:
				try: temp = {'name': place['name'], 'id': place['id'], 'price_level':place['price_level'], 'rating':'NA','types':place['types'], 'vicinity':place['vicinity']}
				except:
					try: temp = {'name': place['name'],'id': place['id'], 'price_level':-1, 'rating':place['rating'], 'types':place['types'], 'vicinity':place['vicinity']}
					except: temp = {'name': place['name'], 'id': place['id'], 'price_level':-1, 'rating':'NA', 'types':place['types'], 'vicinity':place['vicinity']}
			#append
			placeNoMatch.append(temp)
	#examplePlace1 = {'name' : 'FBI Blacksite', 'id' : 'abcdef', 'types' : ['da club', 'blacksite'], 'vicinity' : 'lol cannot say', 'rating' : 3.5, 'price_level' : 2, 'hashtags' : {'BrosOnBros' : 4, 'TheyAreTorturingMe' : 10}}
	#examplePlace2 = {'name' : 'Hot Mamas', 'id' : 'aghijk', 'types' : ['nomnom'], 'vicinity' : 'your mother\'s address', 'rating' : 11, 'price_level' : 0, 'hashtags' : {'BrosOnBros' : 1000000}}
	#examplePlaces = [examplePlace1, examplePlace2]

	context = { 'placeMatch':placeMatch, 'placeNoMatch':placeNoMatch} #'examplePlaces':examplePlaces}
	return render(request, 'places/index.html', context)
	
	
def placeDetail(request,place_id):

	context = {}
	return render(request, 'places/placeDetail.html', context)