from flask import Flask, render_template, request
import json
import sqlite3
import requests
import pandas as pd

app = Flask(__name__)

DATABASE_PATH = '/usr/local/share/OSRS_Dip_Finder/database/ge_prices.db'

@app.route('/get_data', methods=["GET"])
def get_data():

    raw_data = get_recent_data_from_db()
    data = transform_data(raw_data)

    return json.dumps(data)


@app.route('/')
def index():
    return render_template('index.html')


####################################################


def get_recent_data_from_db():

    # query from:
    # https://stackoverflow.com/questions/2129693/using-limit-within-group-by-to-get-n-results-per-group

    #conn = sqlite3.connect('../database/ge_prices.db')
    conn = sqlite3.connect(DATABASE_PATH)

    query_string = """SELECT p.timestamp, i.name, p.id, p.avgHighPrice, p.avgLowPrice, p.highPriceVolume, p.lowPriceVolume
        FROM (
            SELECT *, RANK() OVER (PARTITION BY id ORDER BY timestamp DESC) AS rnk
            FROM prices
        ) AS p
        LEFT JOIN items i
        ON p.id = i.id
        WHERE rnk <= 12;
    """

    df = pd.read_sql_query(query_string, conn)

    return df


def transform_data(data):

    def percentage_difference(num1, num2):
        value = round(((num1 - num2) / num1) * 100, 2)
        return value

    grouped_data = data.groupby('name')

    return_data = {
        'data': []
    }

    for name, group in grouped_data:

        item_data = {
            'id': int(group['id'].mode()),
            'name': name,
            'timestamp': int(group['timestamp'].max())
        }

        low_avg = group['avgLowPrice'].mean()
        low_max = group['avgLowPrice'].max()
        low_min = group['avgLowPrice'].min()
        low_volume_avg = int(group['lowPriceVolume'].mean())
        low_most_recent = group[group['timestamp'] == group['timestamp'].max()]['avgLowPrice'].values[0]

        high_avg = group['avgHighPrice'].mean()
        high_max = group['avgHighPrice'].max()
        high_min = group['avgHighPrice'].min()
        high_volume_avg = int(group['highPriceVolume'].mean())
        high_most_recent = group[group['timestamp'] == group['timestamp'].max()]['avgHighPrice'].values[0]

        low_min_max_diff_percent = percentage_difference(low_max, low_min)
        low_min_max_diff_int = low_max - low_min
        low_recent_to_max_diff_percent = percentage_difference(low_max, low_most_recent)

        high_min_max_diff_percent = percentage_difference(high_max, high_min)
        high_min_max_diff_int = high_max - high_min
        high_recent_to_max_diff_percent = percentage_difference(high_max, high_most_recent)

        item_data['low_avg'] = low_avg
        item_data['low_max'] = low_max
        item_data['low_min'] = low_min
        item_data['low_volume_avg'] = low_volume_avg
        item_data['low_most_recent'] = low_most_recent

        item_data['high_avg'] = high_avg
        item_data['high_max'] = high_max
        item_data['high_min'] = high_min
        item_data['high_volume_avg'] = high_volume_avg
        item_data['high_most_recent'] = high_most_recent

        item_data['low_min_max_diff_percent'] = low_min_max_diff_percent
        item_data['low_min_max_diff_int'] = low_min_max_diff_int
        item_data['low_recent_to_max_diff'] = low_recent_to_max_diff_percent

        item_data['high_min_max_diff_percent'] = high_min_max_diff_percent
        item_data['high_min_max_diff_int'] = high_min_max_diff_int
        item_data['high_recent_to_max_diff'] = high_recent_to_max_diff_percent

        for ele in item_data.keys():
            if pd.isna(item_data[ele]):
                item_data[ele] = -999999

        
     
        if (low_volume_avg > 2000 or high_volume_avg > 2000) and (low_min_max_diff_percent > 3.00 or high_min_max_diff_percent > 3.00) and (high_avg > 100 and low_avg > 100):

            return_data['data'].append(item_data) 
            # print(name)

            # print("")
            # print("Min Max diff (low):", low_min_max_diff_percent, "% | (", low_min, "-", low_max, ")" )
            # print("Min Max diff (high):", high_min_max_diff_percent, "% | (", high_min, "-", high_max, ")" )
            # print("Most recent to max diff % (low):", low_recent_to_max_diff_percent, "% | (", low_most_recent, "-", low_max, ")" )
            # print("Most recent to max diff % (high):", high_recent_to_max_diff_percent, "% | (", high_most_recent, "-", high_max, ")" )
            # print("")
            # print("Low Volume:", low_volume_avg)
            # print("High Volume:", high_volume_avg)

            # print("")
            # print("=================================\n")
            # input()

    return return_data

    
if __name__ == '__main__':
    app.run()
