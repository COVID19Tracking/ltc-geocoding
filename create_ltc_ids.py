import os

from loguru import logger
import googlemaps
import pandas as pd


jsn = os.getenv("LTC_FACILITIES_JSON")
if jsn is None:
    raise ValueError("you must set a value for the LTC_FACILITIES_JSON env variable")

ltc = pd.read_json(jsn)

google_key = os.getenv("GOOGLE_API_KEY")
if google_key is None:
    raise ValueError("you must set a value for the GOOGLE_API_KEY env variable")

gmaps = googlemaps.Client(key=google_key)

def drop_dupes(df):
    df = df.drop_duplicates()
    return df

def create_hash(record):
    record['hash1'] = hash(tuple(record))
    return record

def build_query(record):
    query = ""
    if record["facility_name"]:
        query += record["facility_name"] + ", "
    if record["city"]:
        query += record["city"] + ", "
    if record["county"]:
        query += record["county"] + " County, "
    if record["state"]:
        query += record["state"] + " "
    return query

def geocode(record):
    query = build_query(record)

    try:
        result = gmaps.geocode(query)
    except Exception as err:
        logger.error("google maps call failed for query %s with error: %s" % (query, err))
        return record

    g = result[0]
    if not 'geometry' in g:
        logger.error("could not find coordinates in google map result for query %s" % query)
        return record

    latlon = g.get("geometry").get("location")
    record['address'] = g.get("formatted_address") if g.get("formatted_address") else ''
    record['lat'] = latlon.get("lat") if latlon.get("lat") else ''
    record['lon'] = latlon.get("lng") if latlon.get("lng") else ''
    return record

def main():
    df = ltc[['state', 'county', 'city', 'facility_name']]
    df = drop_dupes(df)
    df = df.apply(create_hash, axis = 1)
    #for testing purposes
    test = df.head(2)
    test = test.apply(geocode, axis = 1)
    test.to_csv('ltc_geocoded_hashed.csv')
    #to run
    # df = df.apply(geocode, axis = 1)
    # df.to_csv('ltc_geocoded_hashed.csv')

if __name__ == "__main__":
    main()

