import os

from loguru import logger
import googlemaps
import pandas as pd
from create_ltc_ids import drop_dupes, create_hash, geocode


jsn = os.getenv("LTC_FACILITIES_JSON")
if jsn is None:
    raise ValueError("you must set a value for the LTC_FACILITIES_JSON env variable")

ltc = pd.read_json(jsn)

geo = os.getenv("LTC_FACILITIES_GEOCODED_CSV")
if geo is None:
    raise ValueError("you must set a value for the LTC_FACILITIES_GEOCODED_CSV env variable")
    
geo = pd.read_csv(geo)
ltc_geo = geo.drop('Unnamed: 0', axis = 1)

google_key = os.getenv("GOOGLE_API_KEY")
if google_key is None:
    raise ValueError("you must set a value for the GOOGLE_API_KEY env variable")

def main():
    fl_ltc = ltc[ltc['state'] == 'FL']
    
    df = fl_ltc[['state', 'county', 'city', 'facility_name']]
    df = drop_dupes(df)
    df = df.apply(create_hash, axis = 1)
    fl_merged = df.reset_index().merge(ltc_geo.set_index('hash'), how='left')
    fl_merged = fl_merged.drop('index', axis = 1)
    fl_merged_geo = fl_merged.apply(geocode, axis = 1)
    frames = [fl_merged_geo, ltc_geo]
    merged = pd.concat(frames)
    merged = drop_dupes(merged)
    merged.to_csv('ltc_geocoded_fl_backfill.csv')

if __name__ == "__main__":
    main()