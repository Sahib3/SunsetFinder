from django.shortcuts import render
from django.http import HttpResponse
import requests
# Create your views here.
#request _>response
#request handler
#action

#example view
def say_hello(request):
    return render(request,"hello.html",{'name':'Mosh'})

    #return HttpResponse('Hello World')
def sunrise_sunset_api(request):
    #Gets the values sent in a http request
    longitude=request.GET.get('longitude', '')
    lattitude=request.GET.get('lattitude', '')
    #gets the sunset data from the sunrisesunset api
    response = requests.get(
    "https://api.sunrisesunset.io/json?lat="+str(lattitude)+"&lng="+str(longitude)+"&timezone=UTC&date=today")

    # print(response)
    #prints response as an HttpResponce object
    return HttpResponse(response)