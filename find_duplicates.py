import json
import pandas as pd

jsn = "/Users/jzarrabi/work/COVID19Tracking/website-data/long_term_care_facilities.json"

def find_duplicates():
    with open(jsn) as f:
        data = json.load(f)
        already_processed = { }
        duplicates = [ ]
        not_found = 0

        for facility in data:
            city = get_elem("city", facility)
            county = get_elem("county", facility)
            state = get_elem("state", facility)
            facility_name = get_elem("facility_name", facility)
            date_outbreak_opened = get_elem("date_outbreak_opened", facility)
            facility_type_state = get_elem("facility_type_state", facility)
            ctp_facility_category = get_elem("ctp_facility_category", facility)
            state_fed_regulated = get_elem("state_fed_regulated", facility)

            if city == "not-found" and county == "not-found" and facility_name == "not-found" and date_outbreak_opened == "not-found" and facility_type_state == "not-found" and ctp_facility_category == "not-found" and state_fed_regulated == "not-found":
                not_found += 1
                continue

            key = "%s%s%s%s%s%s%s%s" % (
                    state,
                    county,
                    city,
                    facility_name,
                    date_outbreak_opened,
                    facility_type_state,
                    ctp_facility_category,
                    state_fed_regulated
                )

            if key in already_processed:
                if already_processed[key] not in duplicates:
                    duplicates.append(already_processed[key])
                duplicates.append(facility)

            already_processed[key] = facility

        with open("duplicates.json", "w") as outfile:
            json.dump(duplicates, outfile)

        print("NUM DUPLICATES: %d" % len(duplicates))
        print("NUM NOTFOUND: %d" % not_found)

def get_elem(name, facility):
    if facility[name]:
        return facility[name]
    return "not-found"


def find_duplicates_pandas():
    ltc = pd.read_json(jsn)
    df = ltc[['state', 'county', 'city', 'facility_name']]
    df['hash'] = df.apply(lambda x: hash(tuple(x)), axis = 1)

    print(df['hash'].duplicated().describe())

find_duplicates()

# find_duplicates_pandas()

