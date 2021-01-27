import os

import pandas as pd

ar_csv = os.getenv("AR_CSV")
nm_csv = os.getenv("NM_CSV")

if (nm_csv is None) and (ar_csv is None):
    raise ValueError("you must set a value for AR_CSV or NM_CSV")

def add_info(record, last_collected, all_data, current_date):
    k = str(record['State']) + str(record['County']) + str(record['City']) + str(record['Facility'])
    if k in last_collected:
        lr = last_collected[k]
        if type(record['County']) is not float and type(record['City']) is not float:
            row = all_data.loc[ (all_data['Date'] == lr) & (all_data['Facility'] == record['Facility']) & (all_data['County'] == record['County'])  & (all_data['City'] == record['City'] )]
        else:
            row = all_data.loc[ (all_data['Date'] == lr) & (all_data['Facility'] == record['Facility'] )]
        record = copy_row(record, row)

        record['last_recorded'] = lr
        record['Date'] = current_date
        record['Outbrk_Status'] = 'Closed'
    else:
        record['last_recorded'] = "Never"

    return record

def add_last_reported_now(record, date):
    record['last_recorded'] = date
    return record

def copy_row(new_row, old_row):
    for c in old_row.columns:
        new_row[c] = old_row.iloc[0][c]
    return new_row

def fill_in_missing(state_csv, state_name):
    print("filling in missing dates for facilities in %s" % state_name)

    filled_in_state = pd.DataFrame()

    all_data = pd.read_csv(state_csv)
    all_data = all_data[all_data['Date'].notna()]

    collection_dates = all_data[['Date']].drop_duplicates()
    facilities = all_data[['State', 'County', 'City', 'Facility']].drop_duplicates()

    last_collected = { }

    for date_index, date_row in collection_dates.iterrows():
        collection_date = date_row['Date']
        current_block = all_data.loc[all_data['Date'] == collection_date]
        for _, block_row in current_block.iterrows():
            k = str(block_row['State']) + str(block_row['County']) + str(block_row['City']) + str(block_row['Facility'])
            last_collected[k] = collection_date

        not_in_block = pd.merge(current_block, facilities, on = ['State', 'County', 'City', 'Facility'], how = 'right', indicator=True).loc[lambda x : x['_merge']=='right_only']
        not_in_block = not_in_block.apply(add_info, axis = 1, args = (last_collected, all_data, collection_date))
        not_in_block = not_in_block[not_in_block['last_recorded'] != "Never"]

        current_block = current_block.apply(add_last_reported_now, axis = 1, args = (collection_date, ) )
        not_in_block = not_in_block.drop(columns = ["_merge"])

        filled_in_state = filled_in_state.append(current_block)
        filled_in_state = filled_in_state.append(not_in_block)

    filled_in_state = filled_in_state.convert_dtypes()
    filled_in_state.reset_index(drop=True, inplace=True)
    filled_in_state.to_csv("filled_in_%s.csv" % state_name, index=False)


def main():
    if nm_csv:
        fill_in_missing(nm_csv, "new_mexico")

    if ar_csv:
        fill_in_missing(ar_csv, "arkansas")

if __name__ == "__main__":
    main()
