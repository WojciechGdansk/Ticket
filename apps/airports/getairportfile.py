import json
import os
from Tickets.settings import API_KEY, AIRPORT_KEY

import requests

# url = "https://airports-iata.p.rapidapi.com/airports"
#
# headers = {
#     "X-RapidAPI-Key": API_KEY,
#     "X-RapidAPI-Host": "airports-iata.p.rapidapi.com"
# }
#
# response = requests.request("GET", url, headers=headers)
#
# with open("/home/wojciech/PycharmProjects/Tickets/airportslist.json", "w") as json_file:
#     json_file.write(response.text)

#
# with open("/home/wojciech/PycharmProjects/Tickets/airportsapi.txt", "w") as f:
#     f.write(response.text)
#
#
# with open("/home/wojciech/PycharmProjects/Tickets/airportsapi.txt", "r") as f:
#     json_object = json.load(f)
    # for item in json_object:
    #     print(item)
    #     print(item['iataCode'])
#

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

