from typing import List
from pydantic import BaseModel, EmailStr

# pydantic models are called schemas = response_models
class S3_Transfer(BaseModel):
    search_method: str
    src_bucket: str
    dest_bucket: str
    dest_folder: str
    prefix: str
    file_name: str

# For filtering to the correct field selection
class Field_Selection(BaseModel):
    table_name: str
    req_value: str
    # list of the input metadata fields
    input_values: dict = {}


class UserRegisterSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    subscription_tier: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserSubscriptionSchema(BaseModel):
    email: EmailStr
    subscription_tier: str
