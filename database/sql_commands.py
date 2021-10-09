##############
## Jay Howard
## 9/29/2021
##
## Purpose: create sqlite3 database (ge_prices.db)
##    Add tables (items and prices) to (ge_prices.db)
##        items: contains the metadata for an item
##        prices: contains price information
##
##    Note:
##        Only the items table is populated if main is called
##        prices is populated by an outside function
##
###############



import ast
import json
import os
import pandas as pd
import requests
import sqlite3
from sqlite3 import Error
import time


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def add_item_table_values():
    """
        Input:
            None
        Note:
            This file is not updated often. The items table will have to be manually dropped for this to update
    """

    try: 

        conn = create_connection(r"ge_prices.db")
        cursor = conn.cursor()

        # if there are already records in the items table, do not insert any new records. This would just create duplicates
        cursor.execute("SELECT COUNT(*) FROM items;")
        records = cursor.fetchall()
        rows_in_items_table = records[0][0]

        if rows_in_items_table > 0:
            print('Items table is already populated')
            return

        # insert individual items into items table
        data = download_item_mapping_from_api()  # get item mapping data from api

        sql_insert_item = """INSERT INTO items (examine, id, members, lowalch, ge_limit, value, highalch, name) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ;"""

        for ele in data:
            if 'limit' not in ele:
                ele['limit'] = None 
            if 'lowalch' not in ele:
                ele['lowalch'] = None
            if 'highalch' not in ele:
                ele['highalch'] = None
            data_tuple = (ele['examine'], ele['id'], ele['members'], ele['lowalch'], ele['limit'], ele['value'], ele['highalch'], ele['name'])
            cursor.execute(sql_insert_item, data_tuple)
        
        conn.commit()

    except sqlite3.Error as error:
        print("Failed to insert Python variable into sqlite table", error)


def add_price_table_values(data):
    """
        Input:
            data: a dictionary that contains the ge price data
        Note: 
            This is called from the download_data.py script
    """

    try: 

        if os.path.isfile('.last_dataset.json'):  # file exists
            with open('.last_dataset.json', 'r') as f:
                old_data = json.loads(f.read())
                if old_data == data:
                    return "Duplicate response values from API - Not updating database"

        conn = create_connection(r"ge_prices.db")
        cursor = conn.cursor()

        sql_insert_item = """INSERT INTO prices (id, timestamp, avgHighPrice, highPriceVolume, avgLowPrice, lowPriceVolume) 
        VALUES (?, ?, ?, ?, ?, ?)
        ;"""

        timestamp = int(time.time())
        for key in data['data'].keys():

            ele = data['data'][key]
            data_tuple = (key, timestamp, ele['avgHighPrice'], ele['highPriceVolume'], ele['avgLowPrice'], ele['lowPriceVolume'])
            cursor.execute(sql_insert_item, data_tuple)
        
        conn.commit()

        with open('.last_dataset.json', 'w') as f:
            json.dump(data, f)

        return 'Data updated'

    except sqlite3.Error as error:
        print("Failed to insert Python variable into sqlite table", error)


def download_item_mapping_from_api():
    url = 'https://prices.runescape.wiki/api/v1/osrs/mapping'

    headers = { 
        'User-Agent': 'Dip finder' 
    }
    response = requests.get(url, headers=headers)
    data_raw = json.loads(response.content)

    return data_raw
        









def main():
    """
        Create the two tables and populate the items table
    """

    sql_create_item_table = """ CREATE TABLE IF NOT EXISTS items (
         examine text NOT NULL,
         id integer NOT NULL,
         members integer NOT NULL,
         lowalch integer,
         ge_limit integer,
         value integer NOT NULL,
         highalch integer,
         name text NOT NULL
    ); """

    sql_create_price_table = """ CREATE TABLE IF NOT EXISTS prices (
         id integer NOT NULL,
         timestamp integer, 
         avgHighPrice integer,
         highPriceVolume integer,
         avgLowPrice integer,
         lowPriceVolume integer
    ); """

    # create connection
    conn = create_connection(r"ge_prices.db")

    # create tables
    cursor = conn.cursor()
    cursor.execute(sql_create_item_table)
    cursor.execute(sql_create_price_table)

    add_item_table_values() # add item data (this only needs to be done once)

    conn.close()


if __name__ == '__main__':
    main()

    # get_recent_data_from_db()
    
    