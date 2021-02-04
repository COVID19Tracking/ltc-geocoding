import pandas as pd

all_data = pd.read_csv("filled_in_arkansas.csv")
# all_data = pd.read_csv("filled_in_new_mexico.csv")

for _, row in all_data.iterrows():
    if row['Date'] < row['last_recorded']:
        raise ValueError("Failure %s" % row)

collection_dates = all_data[['Date']].drop_duplicates()

last_cums = {}
last_cum = 0
for date_index, date_row in collection_dates.iterrows():
    collection_date = date_row['Date']
    current_block = all_data.loc[all_data['Date'] == collection_date]

    cum = current_block['Cume_Res_Pos'].sum()
    if last_cum > cum:
        print("FAILURE ON: %s" % date_row)

    last_cum = cum

    for _, f_row in current_block.iterrows():
        current_cum = f_row['Cume_Res_Pos']
        k = str(f_row['State']) + str(f_row['County']) + str(f_row['City']) + str(f_row['Facility'])
        if k in last_cums:
            if last_cums[k] > current_cum:
                print("on %d %s went from %d to %d" % (collection_date, str(f_row['Facility']), last_cums[k], current_cum))
        last_cums[k] = current_cum
