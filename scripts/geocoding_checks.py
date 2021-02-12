import pandas as pd
from loguru import logger
import googlemaps
import os
import numpy as np


google_key = os.getenv("GOOGLE_API_KEY")
if google_key is None:
    raise ValueError("you must set a value for the GOOGLE_API_KEY env variable")

gmaps = googlemaps.Client(key=google_key)

df = pd.read_csv('~/python/ltc-geocoding/ltc_geocoded_hashed.csv')
df = df.fillna(value='')
ltc = pd.read_json( "~/python/website/_data/long_term_care_facilities.json")


state = pd.read_excel('~/state_abbreviations.xlsx')
state = state.rename(columns={'Abbreviation': 'state', 'Name':'name'})


# to check if address is in the state we expect it to be in
def assert_state(record):
    s = record['state']
    a = record['address']
    n = record['name']

    if s in a:
        record['assert'] = True
    elif n in a:
        record['assert'] = True
    else:
        record['assert'] = False
    return record

test = df
test = test.merge(state, left_on='state', right_on='state', how='left')
test['name'] = test['name'].astype(str)
test = test.apply(assert_state, axis = 1)

# these are ok
t = test[test['assert'] == True]
t = t.drop(['name', 'assert'], axis = 1)

# these should be backfilled manually
mismatch = test[test['assert'] == False]
mismatch.to_csv('~/python/ltc-geocoding/data/mismatch.csv')



def build_query(record):
    query = ""
    if record["facility_name"]:
        query += record["facility_name"] + ", "
    if record["city"]:
        query += record["city"] + ", "
    if record["county"]:
        query += record["county"] + " County, "
    if record["name"]:
        query += record["name"]
    return query


# hits the google geocoding api to find an address and lat/lon for each facility
def geocode(record):
    if(not record['lat'] == ''):
        return record
    query = build_query(record)
    try:
        result = gmaps.geocode(query)
    except Exception as err:
        logger.error("geocode call failed for query %s with error: %s" % (query, err))
        return record

    if not result:
        logger.error("could not find geocode result for query %s" % query)
        return record

    g = result[0]
    if not 'geometry' in g:
        logger.error("could not find coordinates in geocode result for query %s" % query)
        return record

    latlon = g.get("geometry").get("location")
    record['address'] = g.get("formatted_address") if g.get("formatted_address") else ''
    record['lat'] = latlon.get("lat") if latlon.get("lat") else ''
    record['lon'] = latlon.get("lng") if latlon.get("lng") else ''
    return record


# trying to geocode once more, with state names and not abbreviations
to_geo = mismatch

to_geo[['address', 'lat', 'lon']] = ''
    
geocoded = to_geo.apply(geocode, axis = 1)


# to prepare the backfilled addresses for concatenation

backfill = pd.read_excel('~/Downloads/Mismatched States.xlsx')

# Create two lists for the loop results to be placed
lat = []
lon = []

# For each row in a varible,
for row in backfill['latlon']:
    # Try to,
    try:
        # Split the row by comma and append
        # everything before the comma to lat
        lat.append(row.split(',')[0])
        # Split the row by comma and append
        # everything after the comma to lon
        lon.append(row.split(',')[1])
    # But if you get an error
    except:
        # append a missing value to lat
        lat.append(np.NaN)
        # append a missing value to lon
        lon.append(np.NaN)

# Create two new columns from lat and lon
backfill['lat'] = lat
backfill['lon'] = lon
backfill_trimmed = backfill.drop(['latlon','done?','notes','state'], axis = 1)

# here I was lazy and matched these up with their hashes in the original mismatch file

# geocoded mismatched facilities
mis_geo = pd.read_excel('~/python/ltc-geocoding/data/mismatch.xlsx')
mis_geo = mis_geo.drop(['Unnamed: 0','Unnamed: 9','Unnamed: 10'], axis = 1)

# concatenating and writing to file
frames = [t, mis_geo]

geo = pd.concat(frames)
geo.to_csv('~/python/ltc-geocoding/ltc_geocoded_hashed.csv')