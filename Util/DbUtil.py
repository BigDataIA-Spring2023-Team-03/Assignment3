import sqlite3
import boto3
from decouple import config
from botocore.exceptions import ClientError
from Authentication import auth as auth

aws_access_key_id = config('aws_access_key_id')
aws_secret_access_key = config('aws_secret_access_key')
class DbUtil:
    conn = None

    def __init__(self, db_file_name):
        s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        bucket_name = 'damg7245-db'
        s3_file_key = db_file_name

        try:
            s3.Bucket(bucket_name).download_file(s3_file_key, db_file_name)
            import os
            os.chmod(db_file_name, 0o777)
        except ClientError as e:
            print(f"Error downloading file from S3 bucket: {e}")
            raise Exception("Error downloading file from S3 bucket")
        self.conn = sqlite3.connect(db_file_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, *columns):
        query = f'''CREATE TABLE IF NOT EXISTS {table_name} (
                                                {', '.join(columns)}
                                            );'''
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            raise Exception("Error during query execution")

    def alter_table(self, table_name, *columns):
        query = f'''ALTER TABLE {table_name} 
                    ADD COLUMN {', '.join(columns)};'''
        self.cursor.execute(query)
        self.conn.commit()

    # Update Table
    def update_table(self, table_name, update_column, update_value, filter_column, filter):
        query = f'''UPDATE {table_name} 
                    SET {update_column} = '{update_value}'
                    WHERE {filter_column} = '{filter}';'''
        # TESTING
        print(query)

        self.cursor.execute(query)
        self.conn.commit()

    def insert(self, table_name, column_names, list_of_tuples):
        try:
            self.conn.executemany('INSERT INTO {} ({}) VALUES ({})'.format(table_name, ', '.join([i for i in column_names]), ', '.join(['?' for i in range(len(column_names))])), list_of_tuples)
            self.conn.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            raise Exception("Error during query execution")

    def filter(self, table_name, req_value, **input_values):
        try:
            if not input_values:
                query = f'''SELECT DISTINCT {req_value} from {table_name}'''
                self.cursor.execute(query)
            else:
                query = f'''SELECT DISTINCT {req_value} from {table_name}  WHERE'''
                for i in input_values.keys():
                    query += f' {i} = ? AND'
                if query.endswith('AND'):
                    query = query[:-4]
                self.cursor.execute(query, tuple(input_values.values()))
            l = self.cursor.fetchall()
            return sorted([x[0] for x in l])
        except Exception as e:
            print(f"Error executing query: {e}")
            raise Exception("Error during query execution")

    def check_user_registered(self, table_name, email):
        query = f"SELECT email, password_hash FROM {table_name}  WHERE email = '{email}'"
        try:
            self.cursor.execute(query)
            l = self.cursor.fetchall()
            return len(l) > 0 and len(l) == 1
        except Exception as e:
            print(f"Error executing query: {e}")
            raise Exception("Error during query execution")

    def check_user(self, table_name, email, password):
        query = f"SELECT email, password_hash FROM {table_name}  WHERE email = '{email}'"
        try:
            self.cursor.execute(query)
            l = self.cursor.fetchall()
            return len(l) > 0 and len(l) == 1 and auth.verify_password(password, l[0][1])
        except Exception as e:
            print(f"Error executing query: {e}")
            raise Exception("Error during query execution")
        
    def execute_query(self):
        query = "SELECT * from nexrad_lat_long"
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return str(results)
        except Exception as e:
            print(f"Error executing query: {e}")
            raise Exception("Error during query execution")
        
    # CUSTOM QUERIES
    def execute_custom_query(self, query):
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            # return str(results)
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            raise Exception("Error during query execution")
