from datetime import datetime
import json
from os import write
import requests
from sql_commands import add_price_table_values
import time

def download_from_api():
    url = 'https://prices.runescape.wiki/api/v1/osrs/5m'

    headers = {
        'User-Agent': 'Dip finder'
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.content)

    return data


def write_to_log(string):
    with open('download_results.log','a') as f:
        date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        log_string = '{}: {}\n'.format(date_time, string)
        f.write(log_string)


def main():

    while True:
        data = download_from_api()
        return_value = add_price_table_values(data)
        write_to_log(return_value)
        
        print('{}: {}'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), return_value))
        time.sleep(30)


if __name__ == '__main__':
    main()
