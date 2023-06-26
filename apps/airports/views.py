import io
import json
import datetime
import xmltodict
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
from apps.airports.models import Airports
import requests
from Tickets.settings import API_KEY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import random
import string
from django.contrib import messages


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
                "leg_departure_date":
                    get_local_timedate(flightleg['@DepartureDateTime'], flightleg['@FLSDepartureTimeOffset'])[
                        'date'],
                "leg_departure_time":
                    get_local_timedate(flightleg['@DepartureDateTime'], flightleg['@FLSDepartureTimeOffset'])[
                        'time'],
                "depart_from_code": flightleg['DepartureAirport']['@LocationCode'],
                "depart_from_city": flightleg['DepartureAirport']['@FLSLocationName'],
                "leg_arrival_date":
                    get_local_timedate(flightleg['@ArrivalDateTime'], flightleg['@FLSArrivalTimeOffset'])['date'],
                "leg_arrival_time":
                    get_local_timedate(flightleg['@ArrivalDateTime'], flightleg['@FLSArrivalTimeOffset'])['time'],
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


def booking_generator(length=6):
    characters = string.ascii_uppercase + string.digits
    result = "".join(random.choice(characters) for i in range(length))
    return result


def generate_passengers(passengers, startpointX, startpointY, file):
    for item in passengers:
        file.drawString(startpointX, startpointY, f"{item}")
        file.drawString(startpointX + 300, startpointY, "1 bag(s) x 23kg")
        startpointY -= 20
        if startpointY <= 30:
            file.showPage()
            startpointY = 800  # if page breaking point create new page and start from top
    return startpointY


def long_airline_name_break(airline, file, startpointX, startpointY, flightnumber):
    airline = airline.split()
    for item in airline:
        file.drawString(startpointX, startpointY, item)
        startpointY -= 20
    file.drawString(startpointX, startpointY, flightnumber)


def generate_pdf(cleared_names, flight):
    booking = booking_generator()
    airline_reference = booking_generator()
    ticket_name = f"{booking + cleared_names[0]}.pdf"
    plik = io.BytesIO()
    ticket = canvas.Canvas(plik, pagesize=A4)
    ticket.drawImage("/home/wojciech/PycharmProjects/Tickets/apps/airports/static/logowithwhite.jpg", 270, 785,
                     width=50, height=50)
    ticket.drawString(20, 770, "cheaptravel.agency/contact")
    ticket.drawString(100, 800, "CHEAP TRAVEL AGENCY")
    ticket.drawString(400, 800, "TRAVEL DOCUMENT")
    ticket.setFont("Helvetica", 10)
    ticket.drawString(400, 780, f"Order no: {booking}")
    ticket.setFont("Helvetica", 8)
    today = datetime.datetime.today()
    today = datetime.datetime.strftime(today, "%Y-%m-%d")
    ticket.drawString(400, 765, f"Issued: {today}")
    ticket.setLineWidth(.8)
    ticket.line(20, 760, 580, 760)
    ticket.setFont("Helvetica", 20)
    ticket.drawString(50, 730, f"{flight['depart_from_city']} - {flight['arrival_city']}")
    ticket.setLineWidth(.5)
    ticket.line(20, 700, 580, 700)
    ticket.setFont("Helvetica", 12)
    ticket.drawString(50, 680, f"Airline reference check-in: {airline_reference}")
    ticket.drawString(50, 660, f"Your booking number: {booking}")
    ticket.setLineWidth(.8)
    ticket.line(20, 650, 580, 650)
    ticket.drawString(40, 630, "IMPORTANT: PRINT OUT THIS TRAVEL DOCUMENT AND BRING IT WITH YOU ON YOUR")
    ticket.drawString(220, 610, "ALONG WITH YOUR VALID PASSPORT.")
    ticket.drawString(30, 580,
                      "Stay up to date on any schedule changes by checking www.checkmytrip.com or directly via the carrier.")
    ticket.drawString(30, 560, "It is the passenger's responsibility to stay updated on changes of flight times.")
    ticket.line(20, 540, 580, 540)
    if flight['legs'] == 1:
        ticket.setFont("Helvetica", 20)
        ticket.drawString(40, 500, "FLIGHT")
        ticket.drawString(120, 500, "DEPARTURE")
        ticket.drawString(370, 500, "ARRIVAL")
        ticket.setFont("Helvetica", 16)
        long_airline_name_break(flight['details']['1']['airline'], ticket, 40, 470,
                                flight['details']['1']['flight_number'])
        # ticket.drawString(40, 470, f"{flight['details']['1']['airline']}")
        # ticket.drawString(40, 450, f"{flight['details']['1']['flight_number']}")
        ticket.drawString(120, 470, f"{flight['details']['1']['depart_from_city']}")
        ticket.drawString(370, 470, f"{flight['details']['1']['arrival_city']}")
        ticket.setFont("Helvetica", 8)
        ticket.drawString(120, 450, f"{flight['details']['1']['depart_from_code']}")
        ticket.drawString(370, 450, f"{flight['details']['1']['arrival_code']}")
        ticket.setFont("Helvetica", 10)
        ticket.drawString(120, 430, f"{flight['details']['1']['leg_departure_date']}")
        ticket.drawString(370, 430, f"{flight['details']['1']['leg_arrival_date']}")
        ticket.drawString(120, 410, f"{flight['details']['1']['leg_departure_time']}")
        ticket.drawString(370, 410, f"{flight['details']['1']['leg_arrival_time']}")
        ticket.drawString(300, 430, f"{flight['details']['1']['flight_time']}")
        ticket.line(115, 530, 115, 390)
        ticket.drawImage("/home/wojciech/PycharmProjects/Tickets/apps/airports/static/airplane.jpg", 300, 440,
                         width=50, height=50)
        ticket.line(20, 385, 580, 385)
        ticket.drawString(50, 370, f"Passengers:")
        ticket.drawString(350, 370, f"Baggage allowance:")
        new_line_cords_y = generate_passengers(cleared_names, 50, 350, ticket)
        ticket.line(20, new_line_cords_y, 580, new_line_cords_y)

    if flight['legs'] == 2:
        ticket.setFont("Helvetica", 20)
        ticket.drawString(40, 500, "FLIGHT")
        ticket.drawString(120, 500, "DEPARTURE")
        ticket.drawString(370, 500, "ARRIVAL")
        ticket.setFont("Helvetica", 16)
        long_airline_name_break(flight['details'][0]['1']['airline'], ticket, 40, 470,
                                flight['details'][0]['1']['flight_number'])
        ticket.drawString(120, 470, f"{flight['details'][0]['1']['depart_from_city']}")
        ticket.drawString(370, 470, f"{flight['details'][0]['1']['arrival_city']}")
        ticket.setFont("Helvetica", 8)
        ticket.drawString(120, 450, f"{flight['details'][0]['1']['depart_from_code']}")
        ticket.drawString(370, 450, f"{flight['details'][0]['1']['arrival_code']}")
        ticket.setFont("Helvetica", 10)
        ticket.drawString(120, 430, f"{flight['details'][0]['1']['leg_departure_date']}")
        ticket.drawString(370, 430, f"{flight['details'][0]['1']['leg_arrival_date']}")
        ticket.drawString(120, 410, f"{flight['details'][0]['1']['leg_departure_time']}")
        ticket.drawString(370, 410, f"{flight['details'][0]['1']['leg_arrival_time']}")
        ticket.drawString(300, 430, f"{flight['details'][0]['1']['flight_time']}")
        ticket.line(115, 530, 115, 390)
        ticket.drawImage("/home/wojciech/PycharmProjects/Tickets/apps/airports/static/airplane.jpg", 300, 440,
                         width=50, height=50)
        ticket.line(20, 385, 580, 385)
        ticket.drawString(50, 370, f"Passengers:")
        ticket.drawString(350, 370, f"Baggage allowance:")
        new_line_cords_y = generate_passengers(cleared_names, 50, 350, ticket)
        if new_line_cords_y - 250 <= 0:  # if page breaking point create new page and start from top
            ticket.showPage()
            new_line_cords_y = 800
        # Second leg of trip
        ticket.line(20, new_line_cords_y, 580, new_line_cords_y)
        ticket.setFont("Helvetica", 20)
        ticket.drawString(40, new_line_cords_y - 40, "FLIGHT")
        ticket.drawString(120, new_line_cords_y - 40, "DEPARTURE")
        ticket.drawString(370, new_line_cords_y - 40, "ARRIVAL")
        ticket.setFont("Helvetica", 16)
        long_airline_name_break(flight['details'][1]['2']['airline'], ticket, 40, new_line_cords_y - 70,
                                flight['details'][1]['2']['flight_number'])
        ticket.drawString(120, new_line_cords_y - 70, f"{flight['details'][1]['2']['depart_from_city']}")
        ticket.drawString(370, new_line_cords_y - 70, f"{flight['details'][1]['2']['arrival_city']}")
        ticket.setFont("Helvetica", 8)
        ticket.drawString(120, new_line_cords_y - 90, f"{flight['details'][1]['2']['depart_from_code']}")
        ticket.drawString(370, new_line_cords_y - 90, f"{flight['details'][1]['2']['arrival_code']}")
        ticket.setFont("Helvetica", 10)
        ticket.drawString(120, new_line_cords_y - 110, f"{flight['details'][1]['2']['leg_departure_date']}")
        ticket.drawString(370, new_line_cords_y - 110, f"{flight['details'][1]['2']['leg_arrival_date']}")
        ticket.drawString(120, new_line_cords_y - 130, f"{flight['details'][1]['2']['leg_departure_time']}")
        ticket.drawString(370, new_line_cords_y - 130, f"{flight['details'][1]['2']['leg_arrival_time']}")
        ticket.drawString(300, new_line_cords_y - 110, f"{flight['details'][1]['2']['flight_time']}")
        ticket.drawImage("/home/wojciech/PycharmProjects/Tickets/apps/airports/static/airplane.jpg", 300,
                         new_line_cords_y - 100, width=50, height=50)
        ticket.line(20, new_line_cords_y - 155, 580, new_line_cords_y - 155)
        ticket.drawString(50, new_line_cords_y - 170, f"Passengers:")
        ticket.drawString(350, new_line_cords_y - 170, f"Baggage allowance:")
        ticket.line(115, new_line_cords_y - 10, 115, new_line_cords_y - 150)
        new_line_cords_y = generate_passengers(cleared_names, 50, new_line_cords_y - 190, ticket)
    if flight['legs'] == 3:
        ticket.setFont("Helvetica", 20)
        ticket.drawString(40, 500, "FLIGHT")
        ticket.drawString(120, 500, "DEPARTURE")
        ticket.drawString(370, 500, "ARRIVAL")
        ticket.setFont("Helvetica", 16)
        long_airline_name_break(flight['details'][0]['1']['airline'], ticket, 40, 470,
                                flight['details'][0]['1']['flight_number'])
        ticket.drawString(120, 470, f"{flight['details'][0]['1']['depart_from_city']}")
        ticket.drawString(370, 470, f"{flight['details'][0]['1']['arrival_city']}")
        ticket.setFont("Helvetica", 8)
        ticket.drawString(120, 450, f"{flight['details'][0]['1']['depart_from_code']}")
        ticket.drawString(370, 450, f"{flight['details'][0]['1']['arrival_code']}")
        ticket.setFont("Helvetica", 10)
        ticket.drawString(120, 430, f"{flight['details'][0]['1']['leg_departure_date']}")
        ticket.drawString(370, 430, f"{flight['details'][0]['1']['leg_arrival_date']}")
        ticket.drawString(120, 410, f"{flight['details'][0]['1']['leg_departure_time']}")
        ticket.drawString(370, 410, f"{flight['details'][0]['1']['leg_arrival_time']}")
        ticket.drawString(300, 430, f"{flight['details'][0]['1']['flight_time']}")
        ticket.line(115, 530, 115, 390)
        ticket.drawImage("/home/wojciech/PycharmProjects/Tickets/apps/airports/static/airplane.jpg", 300, 440,
                         width=50, height=50)
        ticket.line(20, 385, 580, 385)
        ticket.drawString(50, 370, f"Passengers:")
        ticket.drawString(350, 370, f"Baggage allowance:")
        new_line_cords_y = generate_passengers(cleared_names, 50, 350, ticket)
        if new_line_cords_y - 250 <= 0:  # if page breaking point create new page and start from top
            ticket.showPage()
            new_line_cords_y = 800
        # Second leg of trip
        ticket.line(20, new_line_cords_y, 580, new_line_cords_y)
        ticket.setFont("Helvetica", 20)
        ticket.drawString(40, new_line_cords_y - 40, "FLIGHT")
        ticket.drawString(120, new_line_cords_y - 40, "DEPARTURE")
        ticket.drawString(370, new_line_cords_y - 40, "ARRIVAL")
        ticket.setFont("Helvetica", 16)
        long_airline_name_break(flight['details'][1]['2']['airline'], ticket, 40, new_line_cords_y - 70,
                                flight['details'][1]['2']['flight_number'])
        ticket.drawString(120, new_line_cords_y - 70, f"{flight['details'][1]['2']['depart_from_city']}")
        ticket.drawString(370, new_line_cords_y - 70, f"{flight['details'][1]['2']['arrival_city']}")
        ticket.setFont("Helvetica", 8)
        ticket.drawString(120, new_line_cords_y - 90, f"{flight['details'][1]['2']['depart_from_code']}")
        ticket.drawString(370, new_line_cords_y - 90, f"{flight['details'][1]['2']['arrival_code']}")
        ticket.setFont("Helvetica", 10)
        ticket.drawString(120, new_line_cords_y - 110, f"{flight['details'][1]['2']['leg_departure_date']}")
        ticket.drawString(370, new_line_cords_y - 110, f"{flight['details'][1]['2']['leg_arrival_date']}")
        ticket.drawString(120, new_line_cords_y - 130, f"{flight['details'][1]['2']['leg_departure_time']}")
        ticket.drawString(370, new_line_cords_y - 130, f"{flight['details'][1]['2']['leg_arrival_time']}")
        ticket.drawString(300, new_line_cords_y - 110, f"{flight['details'][1]['2']['flight_time']}")
        ticket.drawImage("/home/wojciech/PycharmProjects/Tickets/apps/airports/static/airplane.jpg", 300,
                         new_line_cords_y - 100, width=50, height=50)
        ticket.line(20, new_line_cords_y - 155, 580, new_line_cords_y - 155)
        ticket.drawString(50, new_line_cords_y - 170, f"Passengers:")
        ticket.drawString(350, new_line_cords_y - 170, f"Baggage allowance:")
        ticket.line(115, new_line_cords_y - 10, 115, new_line_cords_y - 150)
        new_line_cords_y = generate_passengers(cleared_names, 50, new_line_cords_y - 190, ticket)
        if new_line_cords_y - 250 <= 0:  # if page breaking point create new page and start from top
            ticket.showPage()
            new_line_cords_y = 800
        # Third leg of trip
        ticket.line(20, new_line_cords_y, 580, new_line_cords_y)
        ticket.setFont("Helvetica", 20)
        ticket.drawString(40, new_line_cords_y - 40, "FLIGHT")
        ticket.drawString(120, new_line_cords_y - 40, "DEPARTURE")
        ticket.drawString(370, new_line_cords_y - 40, "ARRIVAL")
        ticket.setFont("Helvetica", 16)
        long_airline_name_break(flight['details'][2]['3']['airline'], ticket, 40, new_line_cords_y - 70,
                                flight['details'][2]['3']['flight_number'])
        ticket.drawString(120, new_line_cords_y - 70, f"{flight['details'][2]['3']['depart_from_city']}")
        ticket.drawString(370, new_line_cords_y - 70, f"{flight['details'][2]['3']['arrival_city']}")
        ticket.setFont("Helvetica", 8)
        ticket.drawString(120, new_line_cords_y - 90, f"{flight['details'][2]['3']['depart_from_code']}")
        ticket.drawString(370, new_line_cords_y - 90, f"{flight['details'][2]['3']['arrival_code']}")
        ticket.setFont("Helvetica", 10)
        ticket.drawString(120, new_line_cords_y - 110, f"{flight['details'][2]['3']['leg_departure_date']}")
        ticket.drawString(370, new_line_cords_y - 110, f"{flight['details'][2]['3']['leg_arrival_date']}")
        ticket.drawString(120, new_line_cords_y - 130, f"{flight['details'][2]['3']['leg_departure_time']}")
        ticket.drawString(370, new_line_cords_y - 130, f"{flight['details'][2]['3']['leg_arrival_time']}")
        ticket.drawString(300, new_line_cords_y - 110, f"{flight['details'][2]['3']['flight_time']}")
        ticket.drawImage("/home/wojciech/PycharmProjects/Tickets/apps/airports/static/airplane.jpg", 300,
                         new_line_cords_y - 100, width=50, height=50)
        ticket.line(20, new_line_cords_y - 155, 580, new_line_cords_y - 155)
        ticket.drawString(50, new_line_cords_y - 170, f"Passengers:")
        ticket.drawString(350, new_line_cords_y - 170, f"Baggage allowance:")
        ticket.line(115, new_line_cords_y - 10, 115, new_line_cords_y - 150)
        new_line_cords_y = generate_passengers(cleared_names, 50, new_line_cords_y - 190, ticket)

    ticket.showPage()
    ticket.save()
    plik.seek(0)
    return FileResponse(plik, as_attachment=True, filename=ticket_name)


# Create your views here.

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

        url = f"https://timetable-lookup.p.rapidapi.com/TimeTable/{departure_airport}/{arrival_airport}/{date}/"
        parameter = {"Sort": "Duration"}
        headers = {
            "X-RapidAPI-Key": API_KEY,
            'X-RapidAPI-Host': "timetable-lookup.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=parameter)
        json_data = json.dumps(xmltodict.parse(response.text))
        json_object = json.loads(json_data)

        data_to_present = []
        idenfity = 1
        if "Errors" in json_object['OTA_AirDetailsRS']:
            messages.info(request, "Nie można znaleźc takiego połączenia")
            return redirect(reverse("main_view"))
        for item in json_object['OTA_AirDetailsRS']["FlightDetails"]:
            specific_flight = {
                "id": idenfity,
                "total_trip_time": item['@TotalTripTime'][2:],
                "departure_date": get_local_timedate(item['@FLSDepartureDateTime'], item['@FLSDepartureTimeOffset'])[
                    'date'],
                "departure_time": get_local_timedate(item['@FLSDepartureDateTime'], item['@FLSDepartureTimeOffset'])[
                    'time'],
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
            idenfity += 1
        airport_from = Airports.objects.get(iata=departure_airport)
        context = {'data': data_to_present}
        return render(request, 'results.html', context=context)


class SelectedFlight(View):
    def get(self, request, slug):
        selected_flight = request.GET.get('selected')
        selected_flight = selected_flight.replace("'", '"')
        selected_flight = json.loads(selected_flight)
        return render(request, 'selected_flight.html', context={"data": selected_flight})

    def post(self, request, slug):
        names = request.POST.getlist('nameoftraveler')
        flight = request.POST.get('flightdetails')
        cleared_names = []
        for item in names:
            delete_spaces = item.replace(" ", "")
            if delete_spaces != "":
                item = item.upper()
                cleared_names.append(" ".join(item.split()))
        if len(cleared_names) == 0:
            messages.error(request, "Nie podano żadnego prawidłowego imienia")
            return redirect(f"/results/error?selected={flight}")
        flight = flight.replace("'", '"')
        flight = json.loads(flight)
        return generate_pdf(cleared_names, flight)
