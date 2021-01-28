import os

import pandas as pd


ALL_DATES = [
    20200521, 20200528, 20200604, 20200611, 20200618,
    20200625, 20200702, 20200709, 20200716, 20200723,
    20200730, 20200806, 20200813, 20200820, 20200827,
    20200903, 20200910, 20200917, 20200924, 20201001,
    20201008, 20201015, 20201022, 20201029, 20201105,
    20201112, 20201119, 20201126, 20201203, 20201210,
    20201217, 20201224, 20201231, 20210107, 20210114,
    20210121
]

def fill_in_missing_dates(state_csv, state_name):
    print("filling in missing dates for %s ..." % state_name)

    data = pd.read_csv(state_csv)

    starting_date = data.iloc[0]['Date']
    i = ALL_DATES.index(starting_date) + 1
    data = data.convert_dtypes()
    data = data.astype({'CMS_ID': 'Int64'})

    while i < len(ALL_DATES):
        date = ALL_DATES[i]
        if not (date in data['Date'].values):
            prev_date = ALL_DATES[i - 1]
            new_block = data.loc[data['Date'] == prev_date]
            new_block = new_block.assign(Date=date)

            index_to_put = data.index[data['Date'] == prev_date].tolist()[-1] + len(new_block)
            data = pd.concat([data.iloc[:index_to_put], new_block, data.iloc[index_to_put:]])

        i += 1

    data.reset_index(drop=True, inplace=True)
    data.to_csv("%s_all_dates.csv" % state_name, index=False)

def main():
    state_csv = os.getenv("STATE_CSV")

    if state_csv is None:
        raise ValueError("you must set a value for STATE_CSV")

    if state_csv:
        base=os.path.basename(state_csv)
        fill_in_missing_dates(state_csv, os.path.splitext(base)[0])

if __name__ == "__main__":
    main()
