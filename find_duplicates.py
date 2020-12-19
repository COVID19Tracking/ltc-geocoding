import json
import pandas as pd

jsn = "/Users/jzarrabi/work/COVID19Tracking/website-data/long_term_care_facilities.json"

def find_duplicates():
    with open(jsn) as f:
        data = json.load(f)
        thing = set()

        num_duplicates = 0

        for facility in data:
            all_null = True

            if facility['city']:
                all_null = False
                city = facility['city']
            else:
                city = "no-city"

            if facility['county']:
                all_null = False
                county = facility['county']
            else:
                county = 'no-county'

            if facility['state']:
                state = facility['state']
            else:
                state = 'no-state'

            if facility['facility_name']:
                all_null = False
                name = facility['facility_name']
            else:
                name = 'no-name'

            if all_null:
                continue

            key = state + county + city + name

            if key in thing:
                num_duplicates += 1

            thing.add(key)

        print("NUM DUPLICATES: %d" % num_duplicates)

def find_duplicates_pandas():
    ltc = pd.read_json(jsn)
    df = ltc[['state', 'county', 'city', 'facility_name']]
    df['hash'] = df.apply(lambda x: hash(tuple(x)), axis = 1)

    print(df['hash'].duplicated().describe())

find_duplicates()

# find_duplicates_pandas()

