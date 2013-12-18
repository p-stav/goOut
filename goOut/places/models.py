from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Places(models.Model):
	id = models.charfield(max_length = 50)
	tag = models.CharField(max_length = 50)
	freq = models.IntegerField()
	time = models.DateTimeField()
	score = models.FloatField()
	
	def __unicode__(self):
		return self.id,self.tag

class UserActivity (models.Model):
	uid = models.ForeignKey(User)
	id = models.CharField(max_length=None)
	tag = models.CharField(max_length = 50)
	time = models.DateTimeField()
	
	def __unicode__(self):
		return self.id,self.tag