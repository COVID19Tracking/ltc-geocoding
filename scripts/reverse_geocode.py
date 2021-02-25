import os

from loguru import logger
import googlemaps
import pandas as pd


geo = os.getenv("LTC_FACILITIES_GEOCODED_CSV")
if geo is None:
    raise ValueError("you must set a value for the LTC_FACILITIES_GEOCODED_CSV env variable")

ltc_geo = pd.read_csv(geo)

google_key = os.getenv("GOOGLE_API_KEY")
if google_key is None:
    raise ValueError("you must set a value for the GOOGLE_API_KEY env variable")

gmaps = googlemaps.Client(key=google_key)


# hits the google reverse geocoding api to find an address from lat/lon for each facility
# used for states that do not report city and county per facility
def rev_geocode(record):
    if(record['lat'] == '' or record['lon'] == ''):
        return record
    if(record['geocoded_city'] != '' or record['geocoded_county'] != ''):
        return record
    
    latlon = (record['lat'],record['lon'])
    try:
        result = gmaps.reverse_geocode(latlon)
    except Exception as err:
        logger.error("geocode call failed for facility %s with error: %s" % (record['facility_name'], err))
        return record

    if not result:
        logger.error("could not find geocode result for facility %s" % record['facility_name'])
        return record

    g = result[0]
    if not 'address_components' in g:
        logger.error("could not find reverse geocode results for facility %s" % record['facility_name'])
        return record
    address_components = g.get('address_components')
    city_results = [a for a in address_components if a["types"] == ['locality', 'political']]
    city = city_results[0] if city_results else {}
    county_results = [a for a in address_components if a["types"] == ['administrative_area_level_2', 'political']]
    county = county_results[0] if county_results else {}
    record['geocoded_city'] = city.get('long_name')
    record['geocoded_county'] = county.get('long_name')
    return record


def main():
    # these states do not provide facility location information, so we wish to capture city and county during geocoding
    rev_states =['NM', 'UT', 'IN', 'SC', 'OK', 'VT']
    df = ltc_geo
    df = df.fillna(value='')

    to_rev = df[df['state'].isin(rev_states)]
    rev = to_rev.apply(rev_geocode, axis = 1)
    
    not_rev = df[~df['state'].isin(rev_states)]
    frames = [rev, not_rev]
    df = pd.concat(frames)
    geo = df.sort_values(by=['state','facility_name'])
    
    # writing file
    geo.to_csv('~/python/ltc-geocoding/ltc_geocoded_hashed.csv', index=False)


if __name__ == "__main__":
    main()
