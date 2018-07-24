from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def show(request):
    name = "Myron CJ"
    return HttpResponse("My Name is " + str(name))

def showMap(request):
    return render_to_response('myMap.html')