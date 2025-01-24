import os
from sqlite3 import connect
from typing import List, Dict


schema = {}
schema["usage_metadata"] = [
    ["timestamp","VARCHAR(255)","NOT NULL"], 
    ["token_counter","CHAR(20)"], 
    ["count","INT"]
]

schema["requested_tokens"] = [
    ["model","VARCHAR(255)","NOT NULL"], 
    ["timestamp","VARCHAR(255)","NOT NULL"], 
    ["token_counter","CHAR(20)"], 
    ["count","INT"]
]

def connect_get_cursor(database:str='resources/db/cost/sao-chat-cost.db'):
    global connection_object, cursor_object
    connection_object = connect(database)
    cursor_object = connection_object.cursor()
    return cursor_object

def create_table(table_name:str):
    connect_get_cursor()
    cursor_object.execute(f"DROP TABLE IF EXISTS {table_name};")
    schema_ = ",\n".join([" ".join(_) for _ in schema[table_name]])
    query = f"""CREATE TABLE {table_name} ({schema_});"""
    cursor_object.execute(query)
    connection_object.commit()
    connection_object.close()

def records_transaction(records:List[List], table_name:str):
    connect_get_cursor()
    for record in records:
        values = ", ".join(record)
        query = f"""INSERT INTO {table_name} VALUES ({values});"""
        cursor_object.execute(query)
    connection_object.commit()
    connection_object.close()

def query(query:str):
    connect_get_cursor()
    cursor_object.execute(query)
    records = cursor_object.fetchall()
    connection_object.close()
    return records
