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
		
class Hashtag(models.Model):
	text = models.CharField(max_length=50)
	#mapping = 
	
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

class UserAction (models.Model):
	userID = models.ForeignKey(UserProfile)
	place = models.ForeignKey(Place)
	tag = models.ForeignKey(Hashtag)
	time = models.DateTimeField()
	
	def __unicode__(self):
		return self.userID.user.username + " " + self.place.placeName
		
class UserComment(models.Model):
	comment = models.CharField(max_length=140)
	time = models.DateTimeField()
	User = models.ForeignKey(UserProfile)
	Place = models.ForeignKey(Place)

	def __unicode__(self):
		return self.Place.placeName + "  " + self.comment

class UserFeedback(models.Model):
	feedback = models.TextField(max_length=2000)
	date = models.DateTimeField()
	userID = models.ForeignKey(UserProfile)

	def __unicode__(self):
		return self.feedback


