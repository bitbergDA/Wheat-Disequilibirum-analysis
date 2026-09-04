from geopy.distance import geodesic
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import time

# Countries
countries = ['Spain', 'Slovenia', 'Slovakia', 'Romania', 'Poland', 'Lithuania', 'Latvia', 'Italy', 'Hungary', 'Greece', 'Germany', 'France', 'Finland', 'Estonia', 'Czech Republic', 'Croatia', 'Bulgaria', 'Austria']


geolocator = Nominatim(user_agent="")

coords = {}

for country in countries:
    location = geolocator.geocode(country)
    coords[country] = (location.latitude, location.longitude)
    time.sleep(3)  # be polite to the service

print(coords)
# save coordinates
coordinates = pd.DataFrame(
    [(country, lat, lon) for country, (lat, lon) in coords.items()],
    columns=['country', 'lat', 'lon']
)

coordinates.to_csv(r'../../data/processed/country_coordinates.csv', index=False)
