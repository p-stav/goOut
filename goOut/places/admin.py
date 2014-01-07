from django.contrib import admin
from places.models import UserProfile, Place, Hashtag, PlaceTag, UserAction

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Place)
admin.site.register(Hashtag)
admin.site.register(PlaceTag)
admin.site.register(UserAction)

