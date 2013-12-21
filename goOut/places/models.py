from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Place(models.Model):
	placeId = models.CharField(max_length = 100)
	tag = models.CharField(max_length = 50)
	freq = models.IntegerField()
	time = models.DateTimeField()
	score = models.FloatField()
	
	def __unicode__(self):
		return self.placeId

class UserAction (models.Model):
	uid = models.ForeignKey(User)
	placeId = models.CharField(max_length=100)
	tag = models.CharField(max_length = 50)
	time = models.DateTimeField()
	
	def __unicode__(self):
		return self.uid.username
		
class FavoritePlace(models.Model):
	uid = models.ForeignKey(User)
	placeId = models.CharField(max_length = 100)
	
	def  __unicode__(self):
		return self.placeId
		

class PlaceName(models.Model):
	placeId = models.CharField(max_length = 100)
	placeName = models.CharField(max_length = 50)
	
	def __unicode__(self):
		return self.placeName
		
class Hashtag(models.Model):
	tag=models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.tag
