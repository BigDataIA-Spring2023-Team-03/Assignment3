import streamlit as st
import os
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.errorfactory import ClientError
import webbrowser
from decouple import config
import aws_logging
from Util.DbUtil import *
from Util.S3Util import S3Util
import string
import requests


if 'email' not in st.session_state:
    st.session_state.email = ''

if 'logout_disabled' not in st.session_state:
    st.session_state.logout_disabled = True

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

###################################################################################
# Side Bar
with st.sidebar:
    user = "Not Logged In" if st.session_state.email == "" else st.session_state.email
    st.write(f'Current User: {user}')
    logout_submit = st.button('LogOut', disabled=st.session_state.logout_disabled)
    if logout_submit:
        for key in st.session_state.keys():
            if key == 'login_disabled' or key == 'logout_disabled' or key == 'register_disabled'or key == 'logged_in':
                st.session_state[key] = not st.session_state[key]
            else:
                st.session_state[key] = ''
        st.session_state.login_disabled = False
        st.session_state.register_disabled = False
        st.experimental_rerun()

#########################################

util = DbUtil("metadata.db")

########################################################################################################################
# AWS Destination Credentials:
aws_access_key_id = config('aws_access_key_id')
aws_secret_access_key = config('aws_secret_access_key')

# Destination S3 Directory:
dest_bucket = 'damg7245'
dest_folder = 'assignment1'
########################################################################################################################

st.title('SEVIR Data Fetcher')
if not st.session_state.email == "":
    # SELECT DATASOURCE:
    data_source = st.selectbox('Data Source: ', ['GOES-18 geostationary satellite', 'NEXRAD weather radars'])

    # Search Method:
    search_method = st.selectbox('Search Method: ', ['File Name', 'Field Selection'])

    if data_source == 'GOES-18 geostationary satellite':
        BUCKET_NAME = 'noaa-goes18'
        core_url = 'https://noaa-goes18.s3.amazonaws.com/{product_fn}/{year}/{day_of_year}/{hour}/{file_name}'
        metadata = ['Product', 'Year', 'Day of Year', 'Hour', 'File Name']
        if search_method == 'Field Selection':
            st.markdown(f"""
        URL Format: {core_url}\n
        Required Fields:
        - Product
        - Year
        - Day of Year
        - Hour
        - File Name
        """)
    elif data_source == 'NEXRAD weather radars':
        BUCKET_NAME = 'noaa-nexrad-level2'
        core_url = 'https://noaa-nexrad-level2.s3.amazonaws.com/{year}/{month}/{day}/{nexrad_station}/{file_name}'
        metadata = ['Year', 'Month', 'Day', 'NEXRAD Station', 'File Name']
        if search_method == 'Field Selection':
            st.markdown(f"""
    URL Format: {core_url}\n
    Required Fields:
    - Year
    - Month
    - Day
    - NEXRAD Station
    - File Name
    """)



    first_level = []
    year = []
    months = []
    days = []
    files = []
    files_selected = ""

    first_level.append("")
    year.append("")
    months.append("")
    days.append("")
    files.append("")

    def filename_url_producer(bucket_name, file_name):
        pieces = file_name.split("_")
        if 'nexrad' in bucket_name:
            nexrad_station = pieces[0][0:4]
            year = pieces[0][4:8]
            month = pieces[0][8:10]
            day = pieces[0][10:12]
            time = pieces[1]
            prefix = f'{year}/{month}/{day}/{nexrad_station}/'
            core_url = f'https://noaa-nexrad-level2.s3.amazonaws.com/{year}/{month}/{day}/{nexrad_station}/{file_name}'
        if 'noaa-goes' in bucket_name:
            product = pieces[1]
            product_fn = product[:product.rindex('-')]
            product_fn = product_fn.rstrip(string.digits)
            year = pieces[3][1:5]
            day_of_year = pieces[3][5:8]
            hour = pieces[3][8:10]
            prefix = f'{product_fn}/{year}/{day_of_year}/{hour}/'
            core_url = f'https://noaa-goes18.s3.amazonaws.com/{product_fn}/{year}/{day_of_year}/{hour}/{file_name}'

        return prefix, core_url

    def download_s3_folder(bucket_name, s3_folder, local_dir=None):
        bucket = s3.Bucket(bucket_name)
        # TODO: Only first 5 files for now
        counter = 0
        for obj in bucket.objects.filter(Prefix=s3_folder):
            if counter == 5:
                break
            counter += 1
            target = obj.key if local_dir is None \
                else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            if obj.key[-1] == '/':
                continue
            bucket.download_file(obj.key, target)


    # SEARCH BY FILENAME:
    if search_method == 'File Name':
        st.write('Search by Filename:')
        file_name_input = st.text_input('File Name:')
        # TODO: Need rules on what is a valid file_name input
        if file_name_input:
            aws_logging.write_logs(f'User Input: {file_name_input}')
            # TEST
            # st.write(BUCKET_NAME)
            if ('nexrad' in BUCKET_NAME and file_name_input[0:3] == 'OR_'): # or ('noaa-goes' in BUCKET_NAME and file_name_input[0:3] != 'OR_'):
                # Tips
                st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;">Tip: Change Datasource!</p>', unsafe_allow_html=True)
            else:
                try:
                    prefix, url = filename_url_producer(BUCKET_NAME, file_name_input)
                    st.write("")
                    st.write("Generated URL: " + url)
                    aws_logging.write_logs(f'Generated URL: {url}')
                except Exception as e:
                    error = f"""<p style="font-family:sans-serif; color:Red; font-size: 20px;">File Name Error: Incorrect File Name Format!</p>
                            <p style="font-family:sans-serif; color:Red; font-size: 20px; margin-left: 25px;">- Exception: {e}</p>"""
                    st.markdown(error, unsafe_allow_html=True)


    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

    # Download Entire Folder
    def download_s3_folder(bucket_name, s3_folder, local_dir=None):
        bucket = s3.Bucket(bucket_name)
        # TODO: Only first 5 files for now
        counter = 0
        for obj in bucket.objects.filter(Prefix=s3_folder):
            if counter == 5:
                break
            counter += 1
            target = obj.key if local_dir is None \
                else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            if obj.key[-1] == '/':
                continue
            bucket.download_file(obj.key, target)


    # COPY S3 FILE TO DESTINATION:
    def copy_file_to_dest_s3(src_bucket, dest_bucket, dest_folder, prefix, files_selected):
        # Get S3 File:
        s3_src = boto3.client('s3', config=Config(signature_version=UNSIGNED))

        src_response = s3_src.get_object(Bucket=src_bucket, Key=prefix+files_selected)


        # Upload S3 to Destination:
        s3_dest = boto3.client('s3',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)

        dest_file_name = f'{dest_folder}/{src_bucket}/{files_selected}'

        # Check if file has already beeen transferred
        try:
            s3_dest.head_object(Bucket=dest_bucket, Key=dest_file_name)
            # st.write("""File Transfer Error: File already exists!""")
            error = '<p style="font-family:sans-serif; color:Red; font-size: 20px;">File Transfer Error: File already exists!</p>'
            st.markdown(error, unsafe_allow_html=True)
            # dest_url = """File Transfer Error: File already exists!"""
        except ClientError:
            # Not found
            print("""File doesn't exist""")

            test = s3_dest.upload_fileobj(src_response['Body'], dest_bucket, dest_file_name)

        dest_url = f'https://{dest_bucket}.s3.amazonaws.com/{dest_file_name}'

        return dest_url


    if search_method == 'Field Selection' and data_source == 'GOES-18 geostationary satellite':
        result = s3.list_objects_v2(Bucket=BUCKET_NAME, Delimiter="/")
        folders = [fld["Prefix"] for fld in result["CommonPrefixes"]]
        s3_util = S3Util('s3', BUCKET_NAME)
        for folder in folders:
            first_level.append(folder)

        st.write("Selected Product: ABI-L1b-RadC")

        # year_list =util.filter("geos18", 'year', product='ABI-L1b-RadC')
        # Changed to API Response
        data = {
                "table_name": "geos18",
                "req_value": "year",
                "input_values": {"product": 'ABI-L1b-RadC'}
                }

        # TESTING
        # st.write(f'access_token {st.session_state.access_token}')
        # st.write(data)
        # HANDLING 403 EXCEPTION, DUE TO 5 MIN LOGIN EXPIRATION
        try:
            response = requests.get(url = 'http://backend:8000/field_selection', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
            response.raise_for_status()
            # TEST
            # st.write(response)
            # st.write(response.raise_for_status())
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                st.error("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                st.session_state.logout_disabled = False
                st.error("Forbidden: You do not have permission to access this resource - Sign Back In!")
                st.stop()
            else:
                st.error(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            st.error(f"An error occurred: {err}")

        year_list = response.json().get('Filter List')
        # TESTING
        # st.write(response.json())
        # st.write(year_list)

        year_list.insert(0, "")
        year_selected = st.selectbox(
        f'Please select {metadata[1]}', year_list)

        if year_selected:

            # day_list =util.filter("geos18", 'day_of_year', product='ABI-L1b-RadC', year=year_selected)
            # Changed to API Response
            data = {
                    "table_name": "geos18",
                    "req_value": "day_of_year",
                    "input_values": {"product": 'ABI-L1b-RadC',
                                     'year': year_selected
                                     }
                    }

            try:
                response = requests.get(url = 'http://backend:8000/field_selection', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                if response.status_code == 401:
                    st.error("Unauthorized: Invalid username or password")
                elif response.status_code == 403:
                    st.session_state.logout_disabled = False
                    st.error("Forbidden: You do not have permission to access this resource - Sign Back In!")
                    st.stop()
                else:
                    st.error(f"HTTP error occurred: {err}")
            except requests.exceptions.RequestException as err:
                st.error(f"An error occurred: {err}")
            day_list = response.json().get('Filter List')

            day_list.insert(0, "")
            day_selected = st.selectbox(
            f'Please select {metadata[2]}', day_list)

            if day_selected:
                data = {
                        "table_name": "geos18",
                        "req_value": "hour",
                        "input_values": {"product": 'ABI-L1b-RadC',
                                        'year': year_selected,
                                        'day_of_year': day_selected
                                        }
                        }

                try:
                    response = requests.get(url = 'http://backend:8000/field_selection', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
                    response.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    if response.status_code == 401:
                        st.error("Unauthorized: Invalid username or password")
                    elif response.status_code == 403:
                        st.session_state.logout_disabled = False
                        st.error("Forbidden: You do not have permission to access this resource - Sign Back In!")
                        st.stop()
                    else:
                        st.error(f"HTTP error occurred: {err}")
                except requests.exceptions.RequestException as err:
                    st.error(f"An error occurred: {err}")
                hour_list = response.json().get('Filter List')
                
                hour_list.insert(0, "")
                hour_selected = st.selectbox(f'Please select {metadata[3]}', hour_list)

                if hour_selected:
                    prefix = "ABI-L1b-RadC/"+year_selected+"/"+day_selected+"/"+hour_selected+"/"
                    result = s3.list_objects(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter='/')
                    for item in result['Contents']:
                        file = item['Key']
                        files.append(file)

                    st.write(f'Total Files Available: {len(files)}')

                    for i in range(len(files)):
                        files[i] = files[i].replace(prefix, '')

                    # Download all files in folder
                    files.insert(1, 'Download All Files')

                    files_selected = st.selectbox(
                    f'Please select {metadata[4]}', files)

                    if files_selected == 'Download All Files':
                        result = s3.list_objects(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter='/')
                    for item in result['Contents']:
                        file = item['Key']
                        files.append(file)

                    if files_selected == 'Download All Files':
                        s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
                        # Total Folder Size
                        s3_folder = prefix
                        bytes = sum([object.size for object in s3.Bucket(BUCKET_NAME).objects.filter(Prefix=s3_folder)])
                        st.write(f'Total Folder Size: {round(bytes//1000/1024/1024, 3)} GB')

                        if st.button('Download All Files'):
                            download_s3_folder(BUCKET_NAME, s3_folder, local_dir=None)

                    elif files_selected:
                        user_inputs = ["ABI-L1b-RadC", year_selected, day_selected, hour_selected, files_selected]
                        prefix, url = filename_url_producer(BUCKET_NAME, files_selected)
                        st.write("Generated URL: " + url)
                        st.write("")
                        public_url = s3_util.get_url(*user_inputs)
                        st.write("Public url: " + public_url)
                        st.write("")
                        st.write("URLs match? :")
                        st.write(url == public_url)
                        aws_logging.write_logs(f'User Input: {user_inputs}')
                        aws_logging.write_logs(f'Generated URL: {url}')

                        st.text("")
                        st.text("")
                        st.text("")

    # Determined by search method to pick file_name 
    if 'file_name_input' in locals():
        file_name = file_name_input
        # TODO:
        # prefix = ''
    else:
        file_name = files_selected

#######################################################################################################
    if search_method == 'Field Selection' and data_source == 'NEXRAD weather radars':
        BUCKET_NAME = 'noaa-nexrad-level2'
        s3_util = S3Util('s3', BUCKET_NAME)

        # year_list = util.filter('nexrad', 'year', **{})
        # Changed to API Response
        data = {
                "table_name": "nexrad",
                "req_value": "year",
                "input_values": {}
                }

        # HANDLING 403 EXCEPTION, DUE TO 5 MIN LOGIN EXPIRATION
        try:
            response = requests.get(url = 'http://backend:8000/field_selection', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                st.error("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                st.session_state.logout_disabled = False
                st.error("Forbidden: You do not have permission to access this resource - Sign Back In!")
                st.stop()
            else:
                st.error(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            st.error(f"An error occurred: {err}")
        year_list = response.json().get('Filter List')

        year_list.insert(0, "")
        year_selected = st.selectbox(f'Please select {metadata[0]}', year_list)

        if year_selected:
            data = {
                    "table_name": "nexrad",
                    "req_value": "month",
                    "input_values": {'year': year_selected}
                    }

            try:
                response = requests.get(url = 'http://backend:8000/field_selection', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                if response.status_code == 401:
                    st.error("Unauthorized: Invalid username or password")
                elif response.status_code == 403:
                    st.session_state.logout_disabled = False
                    st.error("Forbidden: You do not have permission to access this resource - Sign Back In!")
                    st.stop()
                else:
                    st.error(f"HTTP error occurred: {err}")
            except requests.exceptions.RequestException as err:
                st.error(f"An error occurred: {err}")
            month_list = response.json().get('Filter List')

            month_list.insert(0, "")
            month_selected = st.selectbox(
            f'Please select {metadata[1]}', month_list)

            if month_selected:
                data = {
                        "table_name": "nexrad",
                        "req_value": "day",
                        "input_values": {'year': year_selected,
                                         'month': month_selected
                                         }
                        }

                try:
                    response = requests.get(url = 'http://backend:8000/field_selection', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
                    response.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    if response.status_code == 401:
                        st.error("Unauthorized: Invalid username or password")
                    elif response.status_code == 403:
                        st.session_state.logout_disabled = False
                        st.error("Forbidden: You do not have permission to access this resource - Sign Back In!")
                        st.stop()
                    else:
                        st.error(f"HTTP error occurred: {err}")
                except requests.exceptions.RequestException as err:
                    st.error(f"An error occurred: {err}")
                day_list = response.json().get('Filter List')

                
                day_list.insert(0, "")
                day_selected = st.selectbox(
                f'Please select {metadata[2]}', day_list)

                if day_selected:
                    data = {
                            "table_name": "nexrad",
                            "req_value": "station",
                            "input_values": {'year': year_selected,
                                            'month': month_selected,
                                            'day': day_selected
                                            }
                            }

                    try:
                        response = requests.get(url = 'http://backend:8000/field_selection', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
                        response.raise_for_status()
                    except requests.exceptions.HTTPError as err:
                        if response.status_code == 401:
                            st.error("Unauthorized: Invalid username or password")
                        elif response.status_code == 403:
                            st.session_state.logout_disabled = False
                            st.error("Forbidden: You do not have permission to access this resource - Sign Back In!")
                            st.stop()
                        else:
                            st.error(f"HTTP error occurred: {err}")
                    except requests.exceptions.RequestException as err:
                        st.error(f"An error occurred: {err}")
                    station_list = response.json().get('Filter List')
                    
                    station_list.insert(0, "")
                    station_selected = st.selectbox(
                    f'Please select {metadata[3]}', station_list)

                    if station_selected:
                        prefix = year_selected +"/"+month_selected+"/"+day_selected+"/"+station_selected+"/"
                        result = s3.list_objects(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter='/')
                        for item in result['Contents']:
                            file = item['Key']
                            files.append(file)

                        st.write(f'Total Files Available: {len(files)}')

                        for i in range(len(files)):
                            files[i] = files[i].replace(prefix, '')

                        files.insert(1, 'Download All Files')

                        files_selected = st.selectbox(
                        f'Please select {metadata[4]}', files)

                        if files_selected == 'Download All Files':
                            s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
                            s3_folder = prefix
                            bytes = sum([object.size for object in s3.Bucket(BUCKET_NAME).objects.filter(Prefix=s3_folder)])
                            st.write(f'Total Folder Size: {round(bytes//1000/1024/1024, 3)} GB')

                            if st.button('Download All Files'):
                                download_s3_folder(BUCKET_NAME, s3_folder, local_dir=None)
                        elif files_selected:
                            user_inputs = [year_selected, month_selected, day_selected, station_selected, files_selected]
                            prefix, url = filename_url_producer(BUCKET_NAME, files_selected)
                            st.write(f'Generated URL: {url}')
                            st.write("")
                            public_url = s3_util.get_url(*user_inputs)
                            st.write("Public url: " + public_url)
                            st.write("")
                            st.write("URLs match? :")
                            st.write(url == public_url)
                            aws_logging.write_logs(f'User Input: {user_inputs}')
                            aws_logging.write_logs(f'Generated URL: {url}')

                            st.text("")
                            st.text("")
                            st.text("")

    if 'file_name_input' in locals():
        file_name = file_name_input
    else:
        file_name = files_selected

    if (search_method == 'File Name' and file_name) or (search_method == 'Field Selection' and file_name):
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Download File'):
                aws_logging.write_logs('User Action: Downloaded File Locally')
                webbrowser.open_new_tab(url)
                st.write('File Downloaded Locally')

        with col2:
            if st.button('Transfer File to S3 Bucket'):
                data = {
                        "search_method": search_method,
                        "src_bucket": BUCKET_NAME,
                        "dest_bucket": dest_bucket,
                        "dest_folder": dest_folder,
                        "prefix": prefix,
                        "file_name": file_name
                        }
                response = requests.post(url = 'http://backend:8000/s3_transfer', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
                if response.status_code == 409:
                    st.error(f'{file_name} already transferred to S3!')
                dest_url = response.json().get('Destination s3 URL')

                aws_logging.write_logs(f'User Action: Transfered file to S3 Bucket - {dest_url}')
                if 'Error' in dest_url:
                    st.write(dest_url)
                st.write(f'Destination s3 URL: {dest_url}')


    util.conn.close()
else:
    st.write('Please Login!')




