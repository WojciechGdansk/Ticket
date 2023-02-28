import json
import os


import requests

url = "https://airports-iata.p.rapidapi.com/airports"

headers = {
    "X-RapidAPI-Key": os.environ.get('RAPID_KEY'),
    "X-RapidAPI-Host": "airports-iata.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)
response = response.json()

with open("/home/wojciech/PycharmProjects/Tickets/airportsapi.txt", "w") as f:
    f.write(response.text)


with open("/home/wojciech/PycharmProjects/Tickets/airportsapi.txt", "r") as f:
    json_object = json.load(f)
    # for item in json_object:
    #     print(item)
    #     print(item['iataCode'])
