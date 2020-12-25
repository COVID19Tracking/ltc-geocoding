import os

from loguru import logger
import googlemaps
import pandas as pd

from create_ltc_ids import drop_dupes, create_hash

google_key = os.getenv("GOOGLE_API_KEY")
if google_key is None:
    raise ValueError("you must set a value for the GOOGLE_API_KEY env variable")

gmaps = googlemaps.Client(key=google_key)

def geocode_address(record):
    query = record["address"]
    try:
        result = gmaps.geocode(query)
    except Exception as err:
        logger.error("geocode call failed for query %s with error: %s" % (query, err))
        return record

    if not result:
        logger.error("could not find coordinates in geocode result for query %s" % query)
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

def generate_records():
    with open("facilities_not_found.txt", "r") as f:
        with open("backfill-address.txt", "r") as b:
            lines = f.read().splitlines()
            addresses = b.read().splitlines()
            records = [ ]
            for i in range(len(lines)):
                info = lines[i].rsplit("query")[1].strip().replace("LLC,", "").split(",")
                record = { }
                record["facility_name"] = info[0]
                record["address"] = addresses[i]
                if "County" in info[1]:
                    record["county"] = info[1]
                    record["state"] = info[2]
                elif len(info) == 2:
                    record["state"] = info[1]
                elif len(info) == 3:
                    record["city"] = info[1]
                    record["state"] = info[2]
                else:
                    record["city"] = info[1]
                    record["county"] = info[2]
                    record["state"] = info[3]
                records.append(record)
    return records

def main():
    records = generate_records()
    df = pd.DataFrame(records)
    df = drop_dupes(df)
    df = df.apply(create_hash, axis = 1)
    df = df.apply(geocode_address, axis = 1)
    df.to_csv('ltc_geocoded_hashed_backfill.csv')


if __name__ == "__main__":
    main()
