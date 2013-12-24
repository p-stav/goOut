from django.shortcuts import render
from urllib import urlopen
import json, pprint

#pip install googlemaps
#import googlemaps

# home/index page. 
def index(request):
	#find curLong + curLat
	#HOW DO YOU DO THIS? Hard code for now
	curLoc = '37.798542,-122.422345'
	
	apiCall = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+curLoc+"&radius=550&types=bar|casino|night_club&sensor=true&key=AIzaSyAWf1WnMo_4s35yeXZ-kZyF-QZ7m5MwqP0";
	
	#grab json object from google Places API
	req = urlopen(apiCall).read()
	places = json.loads(req).get("results")
	
	context = { 'places':places}
	
	return render(request, 'places/index.html', context)