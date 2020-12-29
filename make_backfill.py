import pandas as pd
import numpy as np

ltc_geo = pd.read_csv("ltc_geocoded_hashed.csv")
backfill = pd.read_csv("ltc_geocoded_hashed_backfill.csv")

# reshape backfill to match ltc_geo
backfill = backfill.drop(columns = ['Unnamed: 0'])
backfill = backfill[['state', 'city', 'county', 'facility_name', 'hash', 'address', 'lat', 'lon']]

# update ltc_geo and then revert
ltc_geo.set_index('hash', inplace=True)
ltc_geo.update(backfill.set_index('hash'))
ltc_geo = ltc_geo.reset_index()
ltc_geo = ltc_geo[['state', 'city', 'county', 'facility_name', 'hash', 'address', 'lat', 'lon']]
ltc_geo.to_csv('ltc_geocoded_hashed.csv')
