from django.contrib import admin
from places.models import UserProfile, Place, Hashtag, PlaceTag, UserAction, UserFeedback, UserTag, HashtagCategory, JoinBeta

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Place)
admin.site.register(Hashtag)
admin.site.register(PlaceTag)
admin.site.register(UserAction)
admin.site.register(UserFeedback)
admin.site.register(UserTag)
admin.site.register(HashtagCategory)
admin.site.register(JoinBeta)