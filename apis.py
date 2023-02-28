from Util.DbUtil import DbUtil

from fastapi import FastAPI, Depends, status, HTTPException, Response
import os

print(os.getcwd())
import schemas  # Import from same directory
from Authentication import auth, auth_bearer
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from decouple import config
from datetime import datetime

app = FastAPI()
dbUtil = DbUtil('metadata.db')

########################################################################################################################
# AWS Destination Credentials:
aws_access_key_id = config('aws_access_key_id')
aws_secret_access_key = config('aws_secret_access_key')

# Destination S3 Directory:
dest_bucket = 'damg7245-db'
dest_folder = 'assignment1'

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

file_path = 'metadata.db'
s3_key = 'metadata.db'


########################################################################################################################
@app.get("/")
async def read_main():
    return {"msg": "Hello World"}

########################################################################################################################
# File APIs
@app.post("/s3_transfer", status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth_bearer.JWTBearer())],
          tags=['files'])
# def copy_file_to_dest_s3(src_bucket, dest_bucket, dest_folder, prefix, files_selected):
def copy_file_to_dest_s3(request: schemas.S3_Transfer, response: Response):
    # Get S3 File:
    s3_src = boto3.client('s3', config=Config(signature_version=UNSIGNED))

    if request.search_method == 'Field Selection':
        src_response = s3_src.get_object(Bucket=request.src_bucket, Key=request.prefix + request.file_name)
    elif request.search_method == 'File Name':
        src_response = s3_src.get_object(Bucket=request.src_bucket, Key=request.prefix + request.file_name)

    # Upload S3 to Destination:
    s3_dest = boto3.client('s3',
                           aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key)

    dest_file_name = f'{request.dest_folder}/{request.src_bucket}/{request.file_name}'

    try:
        # raise client error
        s3_dest.head_object(Bucket=request.dest_bucket, Key=dest_file_name)
        # TODO: Conflict, since wfile exists, can add location if needed
        response.status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'{request.file_name} already transferred to S3!')
    except:
        test = s3_dest.upload_fileobj(src_response['Body'], request.dest_bucket, dest_file_name)
        dest_url = f'https://{request.dest_bucket}.s3.amazonaws.com/{dest_file_name}'
        return {'Search Method': request.search_method, 'Destination s3 URL': dest_url}


# GET metadata options for
@app.get("/field_selection", status_code=status.HTTP_200_OK, dependencies=[Depends(auth_bearer.JWTBearer())],
         tags=['files'])
def filter(request: schemas.Field_Selection):
    filter_list = dbUtil.filter(request.table_name, request.req_value, **request.input_values)
    return {'Filter List': filter_list}


########################################################################################################################
# User APIs
@app.post('/user/register', tags=['user'])
def register(user: schemas.UserRegisterSchema):
    if not dbUtil.check_user_registered('users', user.email):
        dbUtil.insert('users', ['first_name', 'last_name', 'email', 'password_hash', 'subscription_tier'],
                      [(user.first_name, user.last_name, user.email, auth.get_password_hash(user.password), user.subscription_tier)])
        with open(file_path, "rb") as f:
            s3.upload_fileobj(f, dest_bucket, s3_key)
    else:
        raise HTTPException(status_code=409, detail='Invalid username and/or password')
    return auth.signJWT(user.email)


@app.post('/user/login', tags=['user'])
def login(user: schemas.UserLoginSchema):
    if dbUtil.check_user('users', user.email, user.password):
        return auth.signJWT(user.email)
    else:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')


# Get Current API Status
# return current status tier and API calls remaining
@app.get('/user/status', tags=['user'], dependencies=[Depends(auth_bearer.JWTBearer())])
def api_status(user: schemas.UserSubscriptionSchema):
    # Get the amount of API Calls remaining in the last hour
    # now = datetime.now()
    # current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    query = f'''SELECT COUNT(*) 
    FROM USER_API 
    WHERE EMAIL = '{user.email}'
            AND DATETIME(TIME_OF_REQUEST) >= DATETIME('{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', '-1 hour')
            AND API_TYPE = 'GET'
            AND API != 'USER_STATUS'
            AND REQUEST_STATUS = 200;'''
    
    curr_api_call_amount = dbUtil.execute_custom_query(query)

    subscription_call_limits = {'Free': 10, 'Gold': 15, 'Platinum': 20}
    api_call_limit = subscription_call_limits[user.subscription_tier]

    # TESTING
    # curr_api_call_amount = 5
    # api_call_limit = subscription_call_limits['Free']

    api_calls_remaining = api_call_limit - curr_api_call_amount
        
    return {'Subscription Tier': user.subscription_tier, 'API Calls Remaining': api_calls_remaining} 


# Upgrade Subscription API
@app.post('/user/subscription_upgrade', tags=['user'], dependencies=[Depends(auth_bearer.JWTBearer())])
def register(user: schemas.UserSubscriptionSchema):
    dbUtil.update_table('users', 'subscription_tier', user.subscription_tier, 'email', user.email)
    with open(file_path, "rb") as f:
        s3.upload_fileobj(f, dest_bucket, s3_key)
    return {'New Subscription Tier': user.subscription_tier}



########################################################################################################################
@app.get('/latlong', tags=['nexrad_radar'])
def execute_query():
    return {"data": dbUtil.execute_query()}
