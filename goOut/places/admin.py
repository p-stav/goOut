from django.contrib import admin
from places.models import 	Place, UserAction, FavoritePlace, PlaceName,Hashtag

# Register your models here.
admin.site.register(Place)
admin.site.register(UserAction)
admin.site.register(FavoritePlace)
admin.site.register(PlaceName)
admin.site.register(Hashtag)