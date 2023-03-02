import json
import os
from Tickets.settings import API_KEY, AIRPORT_KEY

import requests

#function to correct names(api provides ? sometimes instead of normal character)
def correct_name(iatacode):
    url = f"https://aerodatabox.p.rapidapi.com/airports/iata/{iatacode}"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers)
    response = json.loads(response.text)
    correct_airport_name = response['fullName']
    try:
        correct_city = response['municipalityName']
    except KeyError:
        correct_city = correct_airport_name
    return [correct_airport_name, correct_city]



url = "https://airports-iata.p.rapidapi.com/airports"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "airports-iata.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)

with open("/home/wojciech/PycharmProjects/Tickets/airportslist.json", "w") as json_file:
    json_file.write(response.text)


with open("/home/wojciech/PycharmProjects/Tickets/airportslist.json", "r") as f:
    res = f.read()

final = json.loads(res)

final_airports_db = open("/home/wojciech/PycharmProjects/Tickets/finalairports.json", "w")
final_airports_list = []

for item in final:
    try:
        if "?" in item['locationName'] or "?" in item['location']:
            try:
                print(item)
                airport = item['iataCode']
                fixed_names = correct_name(airport)
                item['locationName'] = fixed_names[0]
                item['location'] = fixed_names[1]
                print(item)
                final_airports_list.append(item)
            except:
                continue
        else:
            final_airports_list.append(item)
    except TypeError:
        continue

final_airports_db.write(json.dumps(final_airports_list))
final_airports_db.close()



#API with live search
#
# url = "https://aerodatabox.p.rapidapi.com/airports/search/term"
#
# querystring = {"q":"new","limit":"10"}
#
# headers = {
# 	"X-RapidAPI-Key": API_KEY,
# 	"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
# }
#
# response = requests.request("GET", url, headers=headers, params=querystring)
#
# print(response.text)
# response = response.json()
# print(response['items'])

