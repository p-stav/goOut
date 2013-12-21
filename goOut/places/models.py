from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User)
	points = models.IntegerField()
	
	def __unicode__(self):
		return self.user.username
	
class PlaceName(models.Model):
	placeId = models.CharField(max_length = 100)
	placeName = models.CharField(max_length = 50)
	
	def __unicode__(self):
		return self.placeName
		
class Hashtag(models.Model):
	tag=models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.tag
		
class Place(models.Model):
	placeId = models.ForeignKey(PlaceName)
	tag = models.ForeignKey(Hashtag)
	freq = models.IntegerField()
	time = models.DateTimeField()
	score = models.FloatField()
	
	def __unicode__(self):
		return self.placeId

class UserAction (models.Model):
	uid = models.ForeignKey(UserProfile)
	placeId = models.ForeignKey(PlaceName)
	tag = models.ForeignKey(Hashtag)
	time = models.DateTimeField()
	
	def __unicode__(self):
		return self.uid.user.username
		
class FavoritePlace(models.Model):
	uid = models.ForeignKey(UserProfile)
	placeId = models.ForeignKey(PlaceName)
	
	def  __unicode__(self):
		return self.placeId
		

