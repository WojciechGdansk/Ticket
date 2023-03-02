import json
import requests


def correct_name(iatacode):
    url = f"https://aerodatabox.p.rapidapi.com/airports/iata/{iatacode}"

    headers = {
        "X-RapidAPI-Key": "b5c368ee80msh80c8917c3274faep1be84djsnd2682d017abc",
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

with open("/home/wojciech/PycharmProjects/Tickets/airportslist.json", "r") as f:
    res = f.read()

final = json.loads(res)

final_airports_db = open("/home/wojciech/PycharmProjects/Tickets/finalairports.json", "w")
final_airports_list = []
for item in final:
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

final_airports_db.write(json.dumps(final_airports_list))
final_airports_db.close()


# def fill_database():
#     with open("/home/wojciech/PycharmProjects/Tickets/finalairports.json", "r") as f:
#         result = json.loads(f.read())
#         for item in result:
#             try:
#                 obj = Airports.objects.get(iata=item['iataCode'])
#                 obj.location_name = item['locationName']
#                 obj.city = item['location'],
#                 obj.country = item['country']
#             except Airports.DoesNotExist:
#                 Airports.objects.create(iata=item['iataCode'], location_name=item['locationName'], city=item['location'], country=item['country'])

