import pandas as pd
import gmaps
import requests
import os

GMAPS_API_KEY = os.environ["GMAPS_API_KEY"]
gmaps.configure(api_key=GMAPS_API_KEY)

clubs = pd.read_csv("data/clubs_updated.csv")

def get_country(league_id):
    league_country_dict = {'L1': 'de', 'ES1': 'es', 'GB1': 'gb', 'FR1': 'fr', 'IT1': 'it'}
    return (league_country_dict[league_id])

def get_geocoords(club, country):
    GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    
    params = {
        'address': club,
        'region': country,
        'key': GMAPS_API_KEY
    }
    
    response = requests.get(GOOGLE_MAPS_API_URL, params=params).json()
    print(response)
    result = response['results'][0]

    latitude = result['geometry']['location']['lat']
    longitude = result['geometry']['location']['lng']
    address = result['formatted_address']
    print(f'{club}:\naddress: {address}\nlatitude: {latitude} | longitude: {longitude}')
    return latitude, longitude
    

clubs['latitude'] = None
clubs['longitude'] = None

for ind, row in clubs.iterrows():
    league_id = row['league_id']
    country = get_country(league_id)
    
    club = row['name']
    lat, lon = get_geocoords(club, country)
    clubs.at[ind, 'latitude'] = lat
    clubs.at[ind, 'longitude'] = lon