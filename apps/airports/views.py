import json
import datetime
import xmltodict
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse
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
    def get(self, request, slug):
        search_airport = request.GET.get('airport')
        if "," in search_airport:
            search_airport = search_airport[:3]
            result = Airports.objects.filter(iata=search_airport)

        else:
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


class RoutesSearch(View):
    def get(self, request, slug):
        departure_airport = request.GET.get('depart')
        arrival_airport = request.GET.get('arrive')
        date = request.GET.get('date')
        date = "".join(date.split('-'))

        # url = f"https://timetable-lookup.p.rapidapi.com/TimeTable/{departure_airport}/{arrival_airport}/{date}/"
        # parameter = {"Sort": "Duration"}
        # headers = {
        #     "X-RapidAPI-Key": API_KEY,
        #     'X-RapidAPI-Host': "timetable-lookup.p.rapidapi.com"
        # }
        #
        # response = requests.request("GET", url, headers=headers, params=parameter)
        # json_data = json.dumps(xmltodict.parse(response.text))
        # print(json_data)
        with open("/home/wojciech/PycharmProjects/Tickets/data.json", "r") as f:
            json_object = json.load(f)
        # print(json_object)
        # print(json_object['OTA_AirDetailsRS']["FlightDetails"])
        data_to_present = []
        for item in json_object['OTA_AirDetailsRS']["FlightDetails"]:
            #change utc departure time to local departure time
            local_departure_time = item['@FLSDepartureDateTime']
            offset = item['@FLSDepartureTimeOffset']
            difference = offset[0]
            object_of_utc_departure_time = datetime.datetime.strptime(local_departure_time, "%Y-%m-%dT%H:%M:%S")
            offset = offset[1:3] + ":" + offset[3:]
            object_of_offset = datetime.datetime.strptime(offset, "%H:%M")
            if difference=="+":
                object_of_local_departure_time = object_of_utc_departure_time + datetime.timedelta(hours=object_of_offset.hour, minutes=object_of_offset.minute)
                local_departure_time = datetime.datetime.strftime(object_of_local_departure_time, "%Y-%m-%dT%H:%M")
            elif difference=="-":
                object_of_local_departure_time = object_of_utc_departure_time - datetime.timedelta(hours=object_of_offset.hour, minutes=object_of_offset.minute)
                local_departure_time = datetime.datetime.strftime(object_of_local_departure_time, "%Y-%m-%dT%H:%M")
            print(item)
            print(type(item['@FLSDepartureDateTime']))
            specific_flight = {
                "time_flight": item["@TotalFlightTime"][2:],
                "total_trip_time": item['@TotalTripTime'][2:],
                "departure_time": local_departure_time,


                "test": "ciekawe co bedzie"
            }
            data_to_present.append(specific_flight)
        airport_from = Airports.objects.get(iata=departure_airport)
        print(data_to_present)

        context = {'data': data_to_present}
        # return redirect(reverse("results"))
        return render(request, 'results.html', context=context)

