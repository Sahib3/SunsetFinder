from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
import requests
import json
from . import sunCalc
from suncalc import get_position, get_times
# suncalc is not the same as sunCalc. sunCalc is the list of functions made by loreena. 
# suncalc is a external library that I found. I'm aware that its confusing and should
# probably be changed ¯\_(ツ)_/¯
from datetime import datetime
# Create your views here.
#request _>response
#request handler
#action

#example for passing values to an html template named "hello.html" in the templates folder
def testdex(request, template_name="hello.html"):
    args = {}
    args['name'] = "Johann"
    return TemplateResponse(request, template_name, args)

    #return HttpResponse('Hello World')
def sunrise_sunset_api(request):
    #Gets the values sent in a http request
    longitude=request.GET.get('longitude', '')
    lattitude=request.GET.get('lattitude', '')
    #gets the sunset data from the sunrisesunset api
    response = requests.get(
    "https://api.sunrisesunset.io/json?lat="+str(lattitude)+"&lng="+str(longitude)+"&timezone=UTC&date=today")

    # loads the response as a dictionary into the temp file, then unwraps it into results
    temp=json.loads(response.content)
    results=temp["results"]
    print(str(datetime.now))
    #prints response as an HttpResponce object
    return HttpResponse(results["sunrise"])

def testSunCalc():
        print(sunCalc.calc_approx_atm(7))

def get_azimuth(request):
    year=int(request.GET.get('year', ''))
    month=int(request.GET.get('month', ''))
    day=int(request.GET.get('day', ''))
    hour=int(request.GET.get('hour', ''))
    minute=int(request.GET.get('minute', ''))
    date_and_time=datetime(year,month,day,hour,minute)
    longitude=float(request.GET.get('longitude', ''))
    lattitude=float(request.GET.get('lattitude', ''))
    return HttpResponse(str(get_position(date_and_time,longitude,lattitude)))


