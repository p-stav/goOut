import csv
from django.contrib.auth.models import User
from places.models import Hashtag
import unicodedata
import datetime

HashtagList = []

reader=csv.reader(open("hashtags.csv","r"), delimiter=",")

for hashtag in reader: 
	print hashtag
	
	#modified code from views, submit_submit view
	#new_joke = Joke(owner=User.objects.get(username='pg'), text=joke[0].encode('ascii','replace'), upVotes=0, downVotes=0, date=datetime.datetime.today())
	if not Hashtag.objects.filter(text=hashtag[0]):
		newHashtag = Hashtag(text=hashtag[0])
		newHashtag.save()