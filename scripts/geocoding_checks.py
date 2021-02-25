import pandas as pd
import googlemaps
import os


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