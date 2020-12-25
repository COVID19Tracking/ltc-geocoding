#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 22:56:50 2020

@author: Gilmourj
"""

import pandas as pd
import numpy as np

# to handle batched output
one = pd.read_csv("ltc_geocoded_hashed1.csv")
two = pd.read_csv("ltc_geocoded_hashed2.csv")
three = pd.read_csv("ltc_geocoded_hashed3.csv")

frames = [one, two, three]
df = pd.concat(frames)
export = df.drop('Unnamed: 0', axis = 1)
export = export.reset_index()
export = export[['state', 'city', 'county', 'facility_name', 'hash', 'address', 'lat', 'lon']]

export.to_csv('ltc_geocoded_hashed.csv')

# Data cleaning

#to get state query - will have to handle special casese
df['query_state'] = df['address'].str.slice(-13,-11)

df['same_state'] = np.where(df['state'] == df['query_state'], True, False)

# Fl counties messed up - Dade and Miami-Date so lots of dups 
# We have to watch out, there are some places that have multiple facilities at the same address
# Could probably remove 'facility_name','lat','lon' duplicates relatively safely 
FL = df[df['state'] == 'FL']

# new column with True where vals are duplicated
df['duplicated'] = df.duplicated(subset=['facility_name','lat','lon'], keep=False).describe()
