from django.shortcuts import render
from urllib import urlopen
import json, pprint
from datetime import datetime
from places.models import UserProfile, PlaceName, Hashtag, Place, UserAction, FavoritePlace
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
	
	apiCall = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+curLoc+"&radius=550&types=bar|casino|night_club&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0";
	
	#grab json object from google Places API
	req = urlopen(apiCall).read()
	places = json.loads(req).get("results")
	
	context = { 'places':places}
	
	return render(request, 'places/index.html', context)