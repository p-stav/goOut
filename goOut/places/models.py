from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Place(models.Model):
	placeID = models.CharField(max_length = 100)
	placeName = models.CharField(max_length = 50)
	
	def __unicode__(self):
		return self.placeName

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	points = models.IntegerField()
	favoritePlaces = models.ManyToManyField(Place)
	
	def __unicode__(self):
		return self.user.username

class HashtagCategory(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self):
		return self.name
		
class Hashtag(models.Model):
	text = models.CharField(max_length=50)
	category = models.ForeignKey(HashtagCategory)
	
	def __unicode__(self):
		return self.text

class PlaceTag(models.Model):
	place = models.ForeignKey(Place)
	tag = models.ForeignKey(Hashtag)
	freq = models.IntegerField()
	lastUpdate = models.DateTimeField()
	score = models.FloatField()
	
	def __unicode__(self):
		return self.place.placeName + " " + self.tag.text
		
class UserTag(models.Model):
	userID = models.ForeignKey(UserProfile)
	place = models.ForeignKey(Place)
	tag = models.TextField(max_length=40)
	freq = models.IntegerField()
	lastUpdate = models.DateTimeField()
	score = models.FloatField()

	def __unicode__(self):
		return self.place.placeName + "  " + self.tag

class UserAction (models.Model):
	userID = models.ForeignKey(UserProfile)
	place = models.ForeignKey(Place)
	tags = models.ManyToManyField(Hashtag, blank=True, related_name="useractionHashtag_set")
	userTags = models.ManyToManyField(UserTag, blank = True, related_name="useractionUserTag_set")
	time = models.DateTimeField()
	
	def __unicode__(self):
		return self.userID.user.username + " " + self.place.placeName

class UserFeedback(models.Model):
	feedback = models.TextField(max_length=2000)
	date = models.DateTimeField()
	userID = models.ForeignKey(UserProfile)

	def __unicode__(self):
		return self.feedback

class JoinBeta(models.Model):
	name = models.CharField(max_length=40)
	email = models.CharField(max_length = 100);
	date = models.DateTimeField()
	note = models.TextField(max_length=2000)

	def __unicode__(self):
		return self.name