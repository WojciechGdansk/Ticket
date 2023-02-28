import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from apps.airports.models import Airports
import requests


# Create your views here.
class AirportList(View):
    def get(self, request):
        with open("/home/wojciech/PycharmProjects/Tickets/airportsapi.txt", "r") as f:
            json_object = json.load(f)
            return HttpResponse(json_object)





