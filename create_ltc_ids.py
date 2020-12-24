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
    return df

def build_query(record):
    query = ""
    if record["facility_name"]:
        query += record["facility_name"] + ", "

    if record["city"]:
        query += record["city"] + ", "

    if record["county"]:
        query += record["county"] + " County, "

    if record["state"]:
        query += record["state"] + " "
    return query

    
def geocode(record):
    google_key = os.getenv("GOOGLE_API_KEY")

    query = build_query(record)
    q = quote_plus(query)
    print("query: " + query)
    print(q)
    
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (q, google_key)
    print("url: " + url)
    r = requests.get(url)

    if r.status_code != requests.codes.ok:
        raise ValueError("Expected a 200 from Google but got %d" % r.status_code)
        return record
    r_j = pd.read_json(r.text)
    record['address'] = r_j["results"][0]["formatted_address"]
    record['lat'] = r_j["results"][0]["geometry"]["location"]["lat"]
    record['lon'] = r_j["results"][0]["geometry"]["location"]["lng"]
    return record

def safe_get(record, key):
    return record[key] if record[key] else ""

def generate_row_from_record(record):
    long_lat = geocode(record)
    lat_long = (long_lat[1], long_lat[0])

    uniq_id = hash(lat_long)
    return [uniq_id, safe_get(record, "state"), safe_get(record, "city"), safe_get(record, "county"), safe_get(record, "facility_name"), lat_long]

def main():
    df = drop_dupes()
    test = df.head(2)
    t = test.apply(geocode, axis = 1)
    #df.to_json('ltc_hashed.json')

if __name__ == "__main__":
    main()

