import csv
from django.contrib.auth.models import User
from places.models import Hashtag, HashtagCategory
import unicodedata
import datetime

HashtagList = []

reader=csv.reader(open("hashtags.csv","r"), delimiter=",")

for line in reader: 
	hashtag = line[0]
	category = line[1]

	print hashtag
	print category
	
	if not HashtagCategory.objects.filter(name=category):
		hashtagCategory = HashtagCategory(name=category)
		hashtagCategory.save()
	else:
		hashtagCategory = HashtagCategory.objects.get(name=category)
	if not Hashtag.objects.filter(text=hashtag):
		newHashtag = Hashtag(text=hashtag, category=hashtagCategory)
		newHashtag.save()
	else:
		hashtag = Hashtag.objects.get(text=hashtag)
		hashtag.category = hashtagCategory
		