import os

from loguru import logger
import googlemaps
import pandas as pd


jsn = os.getenv("LTC_FACILITIES_JSON")
if jsn is None:
    raise ValueError("you must set a value for the LTC_FACILITIES_JSON env variable")

ltc = pd.read_json(jsn)

geo = os.getenv("LTC_FACILITIES_GEOCODED_CSV")
if geo is None:
    raise ValueError("you must set a value for the LTC_FACILITIES_GEOCODED_CSV env variable")

ltc_geo = pd.read_csv(geo)

google_key = os.getenv("GOOGLE_API_KEY")
if google_key is None:
    raise ValueError("you must set a value for the GOOGLE_API_KEY env variable")

gmaps = googlemaps.Client(key=google_key)


# creates a unique ID for each facility
def create_hash(record):
    record['hash'] = hash(tuple(record[['state', 'county', 'city', 'facility_name']]))
    return record


# standardizes the facility records
def uppercase(df):
    for colname in ['state', 'county', 'city', 'facility_name']:
        df[colname] = df[colname].str.upper()
    return df


# builds the query string for the geocoding api
def build_query(record):
    query = ""
    if record["facility_name"]:
        query += record["facility_name"] + ", "
    if record["city"]:
        query += record["city"] + ", "
    if record["county"]:
        query += record["county"] + " County, "
    if record["state"]:
        query += record["state"]
    return query
    

# hits the google geocoding api to find an address and lat/lon for each facility
def geocode(record):
    if(not record['lat'] == ''):
        return record
    
    # VT facilities with few or many cases may be named "LONG TERM CARE FACILITY *"
    if(record['state'] == 'VT' and record['facility_name'].find('LONG TERM CARE FACILITY') != -1):
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
    address_components = g.get('address_components')
    latlon = g.get("geometry").get("location")
    record['address'] = g.get("formatted_address") if g.get("formatted_address") else ''
    record['lat'] = latlon.get("lat") if latlon.get("lat") else ''
    record['lon'] = latlon.get("lng") if latlon.get("lng") else ''
    
    city_results = [a for a in address_components if a["types"] == ['locality', 'political']]
    city = city_results[0] if city_results else {}
    county_results = [a for a in address_components if a["types"] == ['administrative_area_level_2', 'political']]
    county = county_results[0] if county_results else {}
    
    record['geocoded_city'] = city.get('long_name')
    record['geocoded_county'] = county.get('long_name')
    return record


def main():
    # latest facility list
    df = ltc[['state', 'county', 'city', 'facility_name']]
    df = df.fillna(value='')
    df = uppercase(df)

    # previously geocoded file
    geo = ltc_geo.drop(['hash'], axis = 1)
    geo = geo.fillna(value='')
    geo = uppercase(geo)

    # concatenating geocoded and non-geocoded facilities
    frames = [df, geo]
    merged = pd.concat(frames)
    merged = merged.drop_duplicates()
    merged = merged.fillna(value='')
    merged['state'] = merged['state'].str.strip()

    # creating hash
    merged = merged.apply(create_hash, axis = 1)

    # dropping facilities if there exists a hash collision (therefore the same facility) and one record is not geocoded
    merged['dup'] = merged.duplicated(subset=['hash'], keep=False)
    merged = merged[(merged['dup'] == False) | (merged['lat'] != '')]
    merged = merged.drop('dup', axis = 1)

    # geocoding
    geocoded = merged.apply(geocode, axis = 1)
    geocoded = geocoded.drop_duplicates()
    df = geocoded[['state','city','county','facility_name','address','lat','lon','hash', 'geocoded_city','geocoded_county']]
    df = df.sort_values(by=['state','facility_name'])
    
    # titlecase county and city
    df['city'] = df['city'].str.title()
    df['county'] = df['county'].str.title()
    
    # removing extra county strings
    df['geocoded_county'] = df['geocoded_county'].str.replace('County', '')
    df['county'] = df['county'].str.replace('County', '')
    
    # writing file
    df.to_csv('~/python/ltc-geocoding/ltc_geocoded_hashed.csv', index=False)


if __name__ == "__main__":
    main()
