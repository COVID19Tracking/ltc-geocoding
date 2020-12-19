import json
import pandas as pd

jsn = "/Users/jzarrabi/work/COVID19Tracking/website-data/long_term_care_facilities.json"

def find_duplicates():
    with open(jsn) as f:
        data = json.load(f)
        already_processed = { }

        num_duplicates = 0

        duplicates = [ ]

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

            if facility['date_outbreak_opened']:
                all_null = False
                date_outbreak_opened = facility['date_outbreak_opened']
            else:
                date_outbreak_opened = 'no-date'

            if all_null:
                continue

            key = "%s%s%s%s%s" % (state, county, city, name, date_outbreak_opened)

            if key in already_processed:
                num_duplicates += 1
                duplicates.append(already_processed[key])
                duplicates.append(facility)

            already_processed[key] = facility

        with open("duplicates.json", "w") as outfile:
            json.dump(duplicates, outfile)

        print("NUM DUPLICATES: %d" % num_duplicates)

def find_duplicates_pandas():
    ltc = pd.read_json(jsn)
    df = ltc[['state', 'county', 'city', 'facility_name']]
    df['hash'] = df.apply(lambda x: hash(tuple(x)), axis = 1)

    print(df['hash'].duplicated().describe())

find_duplicates()

# find_duplicates_pandas()

