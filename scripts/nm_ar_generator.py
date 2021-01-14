import os

import pandas as pd
from datetime import datetime

# ar_csv = os.getenv("AR_CSV")
# if ar_csv is None:
#     raise ValueError("you must set a value for AR_CSV")

nm_csv = os.getenv("NM_CSV")
if nm_csv is None:
    raise ValueError("you must set a value for AR_CSV")


# def convert_date(record):
#     record['datetime'] = datetime.strptime(record['Date Collected'], "%Y%m%d")
#     return record

# ar = pd.read_csv(ar_csv)
# ar.columns = ar.iloc[0]
# ar = ar.drop(ar.index[0])

# collection_dates = ar[['Date Collected']].drop_duplicates()

# facilities = ar[['State ', 'County', 'City', 'Facility Name']].drop_duplicates()
# print(len(facilities))

# # collection_dates = collection_dates.apply(convert_date, axis = 1)
# # ar = ar.apply(convert_date, axis = 1)


# num_date = 0
# current_date = collection_dates.iloc[num_date]['Date Collected']

# first = ar.loc[ar['Date Collected'] == current_date]
# print(first)



# for row in ar.iterrows():
#     if i < len(facilities):
#         date = row[1]['Date Collected']
#         if date != current_date:

def add_last_reported(record, last_recorded_date):
    record['last_recorded'] = last_recorded_date
    return record


def fill_in_missing(state_csv):
    filled_in_state = pd.DataFrame()

    all_data = pd.read_csv(state_csv)
    all_data.columns = all_data.iloc[0]
    all_data = all_data.drop(all_data.index[0])

    collection_dates = all_data[['Date Collected']].drop_duplicates()
    facilities = all_data[['State ', 'County', 'City', 'Facility Name']].drop_duplicates()

    for date_index, date_row in collection_dates.iterrows():
        collection_date = date_row['Date Collected']

        current_block = all_data.loc[all_data['Date Collected'] == collection_date]
        not_in_block = pd.merge(current_block, facilities, on = ['State ', 'County', 'City', 'Facility Name'], how = 'right', indicator=True).loc[lambda x : x['_merge']=='right_only']

        if date_index == 1:
            not_in_block = not_in_block.apply(add_last_reported, axis = 1, args = ('Never', ))

        current_block = current_block.apply(add_last_reported, axis = 1, args = (collection_date, ) )
        not_in_block = not_in_block.drop(columns = ["_merge"])

        filled_in_state = filled_in_state.append(current_block)
        filled_in_state = filled_in_state.append(not_in_block)

        print(filled_in_state)

        return

def main():
    fill_in_missing(nm_csv)

if __name__ == "__main__":
    main()
