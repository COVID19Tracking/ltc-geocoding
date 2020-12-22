#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:51:57 2020

@author: Gilmourj
"""

import numpy as np
import pandas as pd


ltc = pd.read_json("~/python/website/_data/long_term_care_facilities.json")

def create_hash():
    df = ltc[['state', 'county', 'city', 'facility_name','facility_type_state']]
    df['hash'] = df.apply(lambda x: hash(tuple(x)), axis = 1)
    print(df['hash'].duplicated().describe())
    df.to_json('ltc_hashed.json')

def main():
    create_hash()

if __name__ == "__main__":
    main()