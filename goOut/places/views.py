from django.shortcuts import render

# home/index page. 
def index(request):
	context = { }
	return render(request, 'places/index.html', context)