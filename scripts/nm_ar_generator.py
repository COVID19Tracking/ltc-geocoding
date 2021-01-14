import os

import pandas as pd

# ar_csv = os.getenv("AR_CSV")
# if ar_csv is None:
#     raise ValueError("you must set a value for AR_CSV")

nm_csv = os.getenv("NM_CSV")
if nm_csv is None:
    raise ValueError("you must set a value for AR_CSV")

def add_last_reported(record, last_collected):
    if (record['State '], record['County'], record['City'], record['Facility Name']) in last_collected:
        record['last_recorded'] = last_collected[(record['State '], record['County'], record['City'], record['Facility Name'])]
    else:
        record['last_recorded'] = "Never"

    return record

def fill_in_missing(state_csv):
    filled_in_state = pd.DataFrame()

    all_data = pd.read_csv(state_csv)
    all_data.columns = all_data.iloc[0]
    all_data = all_data.drop(all_data.index[0])

    collection_dates = all_data[['Date Collected']].drop_duplicates()
    facilities = all_data[['State ', 'County', 'City', 'Facility Name']].drop_duplicates()

    last_collected = { }

    for date_index, date_row in collection_dates.iterrows():
        collection_date = date_row['Date Collected']

        current_block = all_data.loc[all_data['Date Collected'] == collection_date]
        for _, block_row in current_block.iterrows():
            last_collected[(block_row['State '], block_row['County'], block_row['City'], block_row['Facility Name'])] = collection_date

        not_in_block = pd.merge(current_block, facilities, on = ['State ', 'County', 'City', 'Facility Name'], how = 'right', indicator=True).loc[lambda x : x['_merge']=='right_only']
        not_in_block = not_in_block.apply(add_last_reported, axis = 1, args = (last_collected, ))
        current_block = current_block.apply(add_last_reported, axis = 1, args = (last_collected, ) )
        not_in_block = not_in_block.drop(columns = ["_merge"])

        filled_in_state = filled_in_state.append(current_block)
        filled_in_state = filled_in_state.append(not_in_block)

    filled_in_state.to_csv("filled_in.csv")


def main():
    fill_in_missing(nm_csv)

if __name__ == "__main__":
    main()
