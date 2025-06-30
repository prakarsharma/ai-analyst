import os
from sqlite3 import connect
from contextlib import contextmanager
from typing import List, Dict


from utils.config import conf


schema = {}

schema["cost.requested_tokens"] = [
    ["llm","VARCHAR(255)","NOT NULL"], 
    ["timestamp","VARCHAR(255)","NOT NULL"], 
    ["token_counter","CHAR(20)"], 
    ["count","INT"]
]

schema["eval.evaluated_responses"] = [
    ["task","VARCHAR(255)","NOT NULL"], 
    ["experiment","VARCHAR(255)","NOT NULL"], 
    ["timestamp","VARCHAR(255)","NOT NULL"], 
    ["model","VARCHAR(255)"], 
    ["query","TEXT"], 
    ["response","TEXT"], 
    ["rating","TEXT"], 
    ["score","REAL"], 
    ["reasoning","TEXT"]
]


class Database:
    """
    This class provides an interface to interact with a SQLite database.
    It allows for creating tables, inserting records, and querying data.
    """
    def __init__(self, database_name:str):
        """
        Initializes the Database instance with the table name and retrieves the database path from configurations.
        The table name should be in the format 'database_name.table_name'.
        """
        if "." in database_name:
            self.table_fullname = database_name
            self.DATABASE, self.TABLE = self.table_fullname.split(".")
        else:
            self.DATABASE = database_name
        self.database_path = conf["memory"][self.DATABASE]

    @contextmanager
    def data_definition(self):
        self.connection_object = connect(self.database_path)
        self.cursor_object = self.connection_object.cursor()
        try:
            yield
        finally:
            self.connection_object.commit()
            self.connection_object.close()

    @contextmanager
    def connection(self):
        self.connection_object = connect(self.database_path)
        self.cursor_object = self.connection_object.cursor()
        try:
            yield
        finally:
            self.connection_object.close()

    def create_table(self):
        with self.data_definition():
            query = f"DROP TABLE IF EXISTS {self.TABLE};"
            self.cursor_object.execute(query)

        if self.table_fullname not in schema:
            raise NotImplementedError(f"Schema for table '{self.table_fullname}' not defined.")
        schema_ = ",\n".join([" ".join(_) for _ in schema[self.table_fullname]])

        with self.data_definition():
            query = f"""CREATE TABLE {self.TABLE} ({schema_});"""
            self.cursor_object.execute(query)

    def records_transaction(self, records:List[List]):
        if not os.path.exists(self.database_path):
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
            self.create_table()
        with self.data_definition():
            for record in records:
                values = ", ".join(record)
                query = f"""INSERT INTO {self.TABLE} VALUES ({values});"""
                self.cursor_object.execute(query)

    def query(self, query:str) -> List[Dict]:
        with self.connection():
            self.cursor_object.execute(query)
            records = self.cursor_object.fetchall()
        return records
