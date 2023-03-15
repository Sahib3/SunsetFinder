from django.urls import path
from . import views

#URLConf
urlpatterns =[
    path('hello/', views.testdex),
    # path('sunsetCalc/<int:lattitude>/<int:longitude>', views.sunrise_sunset_api),
    path('sunsetCalc/test', views.sunrise_sunset_api),
    path('sunsetCalc/test2', views.get_azimuth),
]