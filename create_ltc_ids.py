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

jsn = "/Users/jzarrabi/work/COVID19Tracking/website-data/long_term_care_facilities.json"
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

def main():
    df = drop_dupes()
    print(df.iloc[1000])
    print(get_long_lat(df.iloc[1000]))

if __name__ == "__main__":
    main()

