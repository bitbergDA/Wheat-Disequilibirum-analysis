import pandas as pd
import numpy as np
from geopy.distance import geodesic

coordinates = pd.read_csv(r'../../data/processed/country_coordinates.csv')

# Get distance
countries = coordinates['country'].tolist()

distance = pd.DataFrame(
    index=countries,
    columns=countries,
    dtype=float
)

for i in countries:
    for j in countries:
        coord_i = coordinates.loc[
            coordinates['country'] == i, ['lat', 'lon']
        ].values[0]

        coord_j = coordinates.loc[
            coordinates['country'] == j, ['lat', 'lon']
        ].values[0]

        distance.loc[i, j] = geodesic(coord_i, coord_j).km

print(distance)

W = 1 / (distance)

# Set diagonal to zero
W = W.mask(np.eye(W.shape[0], dtype=bool), 0)

# Row-standardize
W = W.div(W.sum(axis=1), axis=0)
#Check that it is standardized
print(W.sum(axis=1))
print(W)

W.to_parquet(r'../../data/processed/W_distance.parquet')