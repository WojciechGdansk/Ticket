import json
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
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


class MainView(View):
    def get(self, request):
        return render(request, 'index.html')


class AirportSearch(View):
    def get(self, request, slug):
        result = Airports.objects.filter(Q(iata__icontains=slug) | Q(city__icontains=slug))
        final_list = []
        for item in result:
            dic = {
                'iata': item.iata,
                'location_name': item.location_name,
                'city': item.city,
                'country': item.country
            }
            final_list.append(dic)
        return JsonResponse({"result": final_list})

