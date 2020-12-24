#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:51:57 2020

@author: Gilmourj
"""

import pandas as pd
import requests
from urllib.parse import quote_plus as quote_plus
import json
import os

jsn = os.getenv("LTC_FACILITIES_JSON")
ltc = pd.read_json(jsn)

def drop_dupes():
    df = ltc[['state', 'county', 'city', 'facility_name']]
    df = df.drop_duplicates()
    return df

def create_hash(df):
    df['hash'] = df.apply(lambda x: hash(tuple(x)), axis = 1)
    df.to_json('ltc_hashed.json')

def get_long_lat(record):
    mapbox_key = os.getenv("MAPBOX_API_KEY")

    query = ""
    if record["facility_name"]:
        query += record["facility_name"] + " "

    if record["city"]:
        query += record["city"] + " "

    if record["county"]:
        query += record["county"] + " "

    if record["state"]:
        query += record["state"] + " "

    if not record["state"] and not record["city"] and record["county"]:
        query += "county "

    q = quote_plus(query)
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places-permanent/%s.json?country=US&access_token=%s" % (q, mapbox_key)
    r = requests.get(url)

    if r.status_code != requests.codes.ok:
        raise ValueError("Expected a 200 from mapbox but got %d" % r.status_code)

    r_json = json.loads(r.text)
    return r_json["features"][0]["geometry"]["coordinates"]

def safe_get(record, key):
    return record[key] if record[key] else ""

def generate_row_from_record(record):
    long_lat = get_long_lat(record)
    lat_long = (long_lat[1], long_lat[0])

    uniq_id = hash(lat_long)
    return [uniq_id, safe_get(record, "state"), safe_get(record, "city"), safe_get(record, "county"), safe_get(record, "facility_name"), lat_long]

def main():
    df = drop_dupes()
    print(df.iloc[1000])
    print(generate_row_from_record(df.iloc[1000]))

if __name__ == "__main__":
    main()

