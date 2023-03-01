import json
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from apps.airports.models import Airports
import requests
from Tickets.settings import API_KEY


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
    def get(self, request):
        search_airport = request.headers['airport']
        result = Airports.objects.filter(Q(iata__icontains=search_airport) | Q(city__icontains=search_airport))
        final_list = []
        for item in result:
            dic = {
                'iata': item.iata,
                'location_name': item.location_name,
                'city': item.city,
                'country': item.country
            }
            final_list.append(dic)
            if len(final_list) == 10:
                break
        return JsonResponse({"result": final_list})



