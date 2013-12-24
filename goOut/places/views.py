from django.shortcuts import render
from urllib import urlopen
import json, pprint

#pip install googlemaps
import googlemaps

# home/index page. 
def index(request):
	#find curLong + curLat
	
	
	#grab json object from google Places API
	#req = 
	
	
	context = { }
	return render(request, 'places/index.html', context)