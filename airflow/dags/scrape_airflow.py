import os
import re
import time
import boto3
import sqlite3
import requests
import pandas as pd
from pathlib import Path
from datetime import timedelta
from airflow.models import DAG
from botocore import UNSIGNED
from botocore.config import Config
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable


dag = DAG(
    dag_id="Metadata_Airflow",
    schedule="0 5 * * *",
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["demo_test", "airflow"],
)

s3client = boto3.client('s3',
                    region_name='us-east-1',
                    config=Config(signature_version=UNSIGNED)
                    )

s3client_private = boto3.client('s3',
                    region_name='us-east-1',
                    aws_access_key_id = Variable.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key = Variable.get('AWS_SECRET_ACCESS_KEY')
                    )

clientLogs = boto3.client('logs',
                region_name='us-east-1',
                aws_access_key_id = os.environ.get('log_aws_access_key_id'),
                aws_secret_access_key = os.environ.get('log_aws_secret_access_key')
                )

def write_logs(message: str):
    clientLogs.put_log_events(
        logGroupName = "Assignment02-logs",
        logStreamName = "Airflow-Logs",
        logEvents = [
            {
                'timestamp' : int(time.time() * 1e3),
                'message' : message
            }
        ]
    )

def scrape_geos18_metadata():
    geos_bucket_name = "noaa-goes18"
    geos18_data_dict = {'product': [], 'year': [], 'day_of_year': [], 'hour': []}
    # write_logs(f"Scraping GEOS18 Metadata into Database")

    prefix = "ABI-L1b-RadC/"
    result = s3client.list_objects(Bucket = geos_bucket_name, Prefix = prefix, Delimiter = '/')
    # write_logs(f"Returning list of objects in GEOS18 Bucket for selected prefix {prefix}: {result}")

    for i in result.get('CommonPrefixes'):
        path = i.get('Prefix').split('/')
        prefix_2 = prefix + path[-2] + "/"
        sub_folder = s3client.list_objects(Bucket = geos_bucket_name, Prefix = prefix_2, Delimiter = '/')
        
        for j in sub_folder.get('CommonPrefixes'):
            sub_path = j.get('Prefix').split('/')
            prefix_3 = prefix_2 + sub_path[-2] + "/"
            sub_sub_folder = s3client.list_objects(Bucket = geos_bucket_name, Prefix = prefix_3, Delimiter = '/')
            
            for k in sub_sub_folder.get('CommonPrefixes'):
                sub_sub_path = k.get('Prefix').split('/')
                sub_sub_path = sub_sub_path[:-1]
                geos18_data_dict['product'].append(sub_sub_path[0])
                geos18_data_dict['year'].append(sub_sub_path[1])
                geos18_data_dict['day_of_year'].append(sub_sub_path[2])
                geos18_data_dict['hour'].append(sub_sub_path[3])
    
    geos18_data = pd.DataFrame(geos18_data_dict)
    # write_logs(f"Returning metadata from GEOS18 Bucket: {geos18_data}")
    
    database_file_name = 'metadata.db'
    ddl_file_name = 'airflow_geos18.sql'
    table_name = 'geos18'

    database_file_path = os.path.join(os.path.dirname(__file__), database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__), ddl_file_name)
    db = sqlite3.connect(database_file_path)

    if Path(database_file_path).is_file():
        # write_logs(f"Database file found, saving GEOS18 metadata into GEOS18 Table")
        geos18_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
    
    else:
        # write_logs(f"Database file not found, initializing database {database_file_name} and updating data into GEOS18 Table.")
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()        
        geos18_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
        cursor.executescript(sql_script)
    
    db.commit()
    db.close()
    # write_logs(f"Successfully Scraped GEOS18 Metadata and stored to Database file.")

def write_db_to_s3():
    file_path = './dags/metadata.db'
    with open(file_path, "rb") as f:
        s3client_private.upload_fileobj(f, 'damg7245-db', 'metadata.db')


def scrape_nexrad_metadata():
    nexrad_bucket_name = "noaa-nexrad-level2"
    nexrad_data_dict = {'year': [], 'month': [], 'day': [], 'station': []}
    # write_logs(f"Scraping NexRad Metadata into Database")

    id = 1
    years = ['2022','2023']
    for year in years:
        prefix = year + '/'
        result = s3client.list_objects(Bucket = nexrad_bucket_name, Prefix = prefix, Delimiter = '/')
        # write_logs(f"Returning list of objects in NEXRAD Bucket for selected prefix {prefix}: {result}")

        for i in result.get('CommonPrefixes'):
            path = i.get('Prefix').split('/')
            prefix_2 = prefix + path[-2] + "/"
            sub_folder = s3client.list_objects(Bucket = nexrad_bucket_name, Prefix = prefix_2, Delimiter = '/')
            
            for j in sub_folder.get('CommonPrefixes'):
                sub_path = j.get('Prefix').split('/')
                prefix_3 = prefix_2 + sub_path[-2] + "/"
                sub_sub_folder = s3client.list_objects(Bucket = nexrad_bucket_name, Prefix = prefix_3, Delimiter = '/')

                for k in sub_sub_folder.get('CommonPrefixes'):
                    sub_sub_path = k.get('Prefix').split('/')
                    sub_sub_path = sub_sub_path[:-1]
                    nexrad_data_dict['year'].append(sub_sub_path[0])
                    nexrad_data_dict['month'].append(sub_sub_path[1])
                    nexrad_data_dict['day'].append(sub_sub_path[2])
                    nexrad_data_dict['station'].append(sub_sub_path[3])
                    id += 1
    
    nexrad_data = pd.DataFrame(nexrad_data_dict)
    # write_logs(f"Returning metadata from NEXRAD Bucket: {nexrad_data}")

    database_file_name = 'metadata.db'
    ddl_file_name = 'airflow_nexrad.sql'
    table_name = 'nexrad'

    database_file_path = os.path.join(os.path.dirname(__file__), database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__), ddl_file_name)
    db = sqlite3.connect(database_file_path)
    
    if Path(database_file_path).is_file():
        # write_logs(f"Database file found, saving NEXRAD metadata into NEXRAD Table")
        nexrad_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
    
    else:
        # write_logs(f"Database file not found, initializing database {database_file_name} and updating data into NEXRAD Table.")
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()        
        nexrad_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
        cursor.executescript(sql_script)
        
    db.commit()
    db.close()
    # write_logs(f"Successfully Scraped NEXRAD Metadata and stored to Database file.")
    # return nexrad_data

def scrape_nexradmap_metadata():
    nexrad_map_data_url = "https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt"
    nexradmap_data_dict = {'station': [], 'LAT': [], 'LONG': [], 'city': []}
    # write_logs(f"Scraping NexRadMap Metadata into Database")

    try:
        response = requests.get(nexrad_map_data_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err_http:
        write_logs(f"Exited due to HTTP error while accessing URL")
        raise SystemExit(err_http)
    except requests.exceptions.ConnectionError as err_conn:
        write_logs(f"Exited due to Connection error while accessing URL")
        raise SystemExit(err_conn)
    except requests.exceptions.Timeout as err_tim:
        write_logs(f"Exited due to Timeout error while accessing URL")
        raise SystemExit(err_tim)
    
    lines = response.text.split('\n')
    id = 0
    nexradmap = []
    for line in lines:
        line = line.strip()
        word_list = line.split(" ")
        if (word_list[-1].upper() == 'NEXRAD'):
            nexradmap.append(line)
    nexradmap = [i for i in nexradmap if 'UNITED STATES' in i]
    
    for station in nexradmap:
        id += 1
        station1 = station.split("  ")
        station1 =  [i.strip() for i in station1 if i != ""]
        station2 = station.split(" ")
        station2 =  [i.strip() for i in station2 if i != ""]
        nexradmap_data_dict['station'].append(station1[0].split(" ")[1])
        for i in range(len(station1)):
            if (re.match(r'\b[A-Z][A-Z]\b',station1[i].strip())):
                nexradmap_data_dict['city'].append(station1[i][2:])
        for i in range(len(station2)):
            if (re.match(r'^-?[0-9]\d(\.\d+)?$',station2[i])):
                nexradmap_data_dict['LAT'].append(float(station2[i]))
                nexradmap_data_dict['LONG'].append(float(station2[i+1]))
                break
    
    nexradmap_data = pd.DataFrame(nexradmap_data_dict)
    # write_logs(f"Returning metadata for NEXRAD Map Locations: {nexradmap_data}")

    database_file_name = 'metadata.db'
    ddl_file_name = 'airflow_nexradmap.sql'
    table_name = 'nexrad_lat_long'

    database_file_path = os.path.join(os.path.dirname(__file__), database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__), ddl_file_name)
    db = sqlite3.connect(database_file_path)
    
    if Path(database_file_path).is_file():
        # write_logs(f"Database file found, saving NEXRAD metadata into NEXRAD Table")
        nexradmap_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
    
    else:
        # write_logs(f"Database file not found, initializing database {database_file_name} and updating data into NEXRAD Table.")
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()        
        nexradmap_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
        cursor.executescript(sql_script)
        
    db.commit()
    db.close()

with dag:

    scrape_geos18 = PythonOperator(
    task_id='scrape_geos18',
    python_callable = scrape_geos18_metadata,
    provide_context=True,
    dag=dag,
    )

    scrape_nexrad = PythonOperator(
    task_id='scrape_nexrad',
    python_callable = scrape_nexrad_metadata,
    provide_context=True,
    dag=dag,
    )

    scrape_nexradmap = PythonOperator(
    task_id='scrape_nexradmap',
    python_callable = scrape_nexradmap_metadata,
    provide_context=True,
    dag=dag,
    )

    write_db_to_s3 = PythonOperator(
        task_id='write_db_to_s3',
        python_callable=write_db_to_s3,
        provide_context=True,
        dag=dag,
    )

    scrape_geos18 >> scrape_nexrad >> scrape_nexradmap >> write_db_to_s3