from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Places(models.Model):
	placeId = models.CharField(max_length = 100)
	tag = models.CharField(max_length = 50)
	freq = models.IntegerField()
	time = models.DateTimeField()
	score = models.FloatField()
	
	def __unicode__(self):
		return self.placeId,self.tag

class UserActivity (models.Model):
	uid = models.ForeignKey(User)
	placeId = models.CharField(max_length=100)
	tag = models.CharField(max_length = 50)
	time = models.DateTimeField()
	
	def __unicode__(self):
		return self.placeId,self.tag
		
class favoritePlaces(models.Model):
	uid = models.ForeignKey(User)
	placeId = models.CharField(max_length = 100)
	
	def  __unicode__(self):
		return self.uid.firstName,self.placeId
		

class placeNames(models.Model):
	placeId = models.CharField(max_length = 100)
	placeName = models.CharField(max_length = 50)
	
	def __unicode__(self):
		return self.placeId