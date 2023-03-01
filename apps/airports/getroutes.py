import json
import requests
import os
from Tickets.settings import API_KEY
import xmltodict

# url = "https://timetable-lookup.p.rapidapi.com/TimeTable/BOS/LAX/20230317/"
#
# headers = {
#     "X-RapidAPI-Key": API_KEY,
#     'X-RapidAPI-Host': "timetable-lookup.p.rapidapi.com"
# }
#
# response = requests.request("GET", url, headers=headers)
#
# json_data = json.dumps(xmltodict.parse(response.text))
#
# with open("/home/wojciech/PycharmProjects/Tickets/data.json", "w") as json_file:
#     json_file.write(json_data)


with open("/home/wojciech/PycharmProjects/Tickets/data.json", "r") as f:
    json_object = json.load(f)
    # print(json_object['OTA_AirDetailsRS']["FlightDetails"])
    for item in json_object['OTA_AirDetailsRS']["FlightDetails"]:
        print(item)

