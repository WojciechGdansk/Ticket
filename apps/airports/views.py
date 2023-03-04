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


# change utc time to local time
def get_local_timedate(date, offset):
    local_departure_time = date
    dif = offset
    difference = dif[0]
    object_of_utc_departure_time = datetime.datetime.strptime(local_departure_time, "%Y-%m-%dT%H:%M:%S")
    dif = dif[1:3] + ":" + dif[3:]
    object_of_offset = datetime.datetime.strptime(dif, "%H:%M")
    if difference == "+":
        object_of_local_departure_time = object_of_utc_departure_time + datetime.timedelta(hours=object_of_offset.hour,
                                                                                           minutes=object_of_offset.minute)
        local_departure_time = datetime.datetime.strftime(object_of_local_departure_time, "%Y-%m-%dT%H:%M")
    elif difference == "-":
        object_of_local_departure_time = object_of_utc_departure_time - datetime.timedelta(hours=object_of_offset.hour,
                                                                                           minutes=object_of_offset.minute)
        local_departure_time = datetime.datetime.strftime(object_of_local_departure_time, "%Y-%m-%dT%H:%M")

    return {"date": local_departure_time[:10],
            "time": local_departure_time[11:]}


def time_of_flight(totaltriptime):
    hours = totaltriptime[2:].split("H")[0]
    minutes = totaltriptime[:-1].split("H")[1]
    return [hours, minutes]


def prepare_flight_details(flightleg):


    if type(flightleg) is dict:

        result = {
            flightleg['@SequenceNumber']: {
                "leg_departure_date": get_local_timedate(flightleg['@DepartureDateTime'], flightleg['@FLSDepartureTimeOffset'])[
                    'date'],
                "leg_departure_time": get_local_timedate(flightleg['@DepartureDateTime'], flightleg['@FLSDepartureTimeOffset'])[
                    'time'],
                "depart_from_code": flightleg['DepartureAirport']['@LocationCode'],
                "depart_from_city": flightleg['DepartureAirport']['@FLSLocationName'],
                "leg_arrival_date": get_local_timedate(flightleg['@ArrivalDateTime'], flightleg['@FLSArrivalTimeOffset'])['date'],
                "leg_arrival_time": get_local_timedate(flightleg['@ArrivalDateTime'], flightleg['@FLSArrivalTimeOffset'])['time'],
                "arrival_code": flightleg['ArrivalAirport']['@LocationCode'],
                "arrival_city": flightleg['ArrivalAirport']['@FLSLocationName'],
                "flight_time": flightleg['@JourneyDuration'][2:],
                "flight_number": flightleg['@FlightNumber'],
                "airline": flightleg['MarketingAirline']['@CompanyShortName']
            }
        }
        return result
    else:
        final = []
        for leg in flightleg:
            final.append(prepare_flight_details(leg))

    return final


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
        # with open("/home/wojciech/PycharmProjects/Tickets/data2.json", "w") as json_file:
        #     json_file.write(json_data)

        with open("/home/wojciech/PycharmProjects/Tickets/data2.json", "r") as f:
            json_object = json.load(f)

        print(json_object)
        data_to_present = []
        idenfity = 1
        for item in json_object['OTA_AirDetailsRS']["FlightDetails"]:
            specific_flight = {
                "id": idenfity,
                "total_trip_time": item['@TotalTripTime'][2:],
                "departure_date": get_local_timedate(item['@FLSDepartureDateTime'], item['@FLSDepartureTimeOffset'])['date'],
                "departure_time": get_local_timedate(item['@FLSDepartureDateTime'], item['@FLSDepartureTimeOffset'])['time'],
                "depart_from_code": item["@FLSDepartureCode"],
                "depart_from_city": item['@FLSDepartureName'],
                "arrival_date": get_local_timedate(item['@FLSArrivalDateTime'], item['@FLSArrivalTimeOffset'])['date'],
                "arrival_time": get_local_timedate(item['@FLSArrivalDateTime'], item['@FLSArrivalTimeOffset'])['time'],
                "arrival_code": item['@FLSArrivalCode'],
                "arrival_city": item['@FLSArrivalName'],
                "legs": int(item['@FLSFlightLegs']),
                'details': prepare_flight_details(item['FlightLegDetails']),
            }
            data_to_present.append(specific_flight)
            idenfity +=1
        airport_from = Airports.objects.get(iata=departure_airport)
        print(data_to_present)

        context = {'data': data_to_present}
        # return redirect(reverse("results"))
        return render(request, 'results.html', context=context)

