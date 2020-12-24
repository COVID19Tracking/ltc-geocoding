#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:51:57 2020

@author: Gilmourj
"""

import pandas as pd

ltc = pd.read_json("~/python/website/_data/long_term_care_facilities.json")

def drop_dupes():
    df = ltc[['state', 'county', 'city', 'facility_name']]
    df = df.drop_duplicates()
    return df
    
def create_hash(df):
    df['hash'] = df.apply(lambda x: hash(tuple(x)), axis = 1)
    df.to_json('ltc_hashed.json')

def main():
    df = drop_dupes()
    create_hash(df)

if __name__ == "__main__":
    main()
