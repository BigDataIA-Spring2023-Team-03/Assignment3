import typer
from dotenv import load_dotenv
from dataclasses import dataclass
import requests
import json
from enum import Enum 

load_dotenv()

app = typer.Typer(add_completion=False)


@dataclass
class Common:
    email: str
    password: str


@app.command()
def feild_selection(ctx: typer.Context, table_name: str, req_value: str):

    logged_in = False
    url = "http://localhost:8000"
    access_token = ""
    post = "/user/login"
    url_call = url + post
    body = {
    "email": ctx.obj.email,
    "password": ctx.obj.password
    }

    response = requests.post(url_call, json=body)

    if response.status_code == 405:
        typer.echo(response.json())  
    else:
        typer.echo("Login Successfull")
        res = response.json()
        logged_in = True
        access_token = access_token + res["access_token"]
        typer.echo(f"Access Token is {access_token}")

    if logged_in:
        # post = "/fieldselection"
        # url_call = url + post
        # headers = {}
        # headers['Authorization'] = f"Bearer {access_token}"
        # payload = json.dumps({
        #     "table_name": table_name,
        #     "req_value": req_value,
        #     "input_values": input_values
        # })
        # response = requests.request("GET", url_call, headers=headers, data=payload)
        # if response.status_code == 200:
        #     typer.echo("Success") # request success
        #     typer.echo("\n",response.json())
        # else:
        #     typer.echo("\nFailed to get response") # request failed
        input_values ={}
        if req_value == "year":
            product = typer.prompt("What's the product you are looking for?")
            input_values = {"product": str(product)}
        elif req_value == "dayofyear":
            product = typer.prompt("What's the product you are looking for?")
            year = typer.prompt("What's the year?")
            input_values = {"product": str(product),
                            "year": str(year)}
        elif req_value == "hour":
            product = typer.prompt("What's the product you are looking for?")
            year = typer.prompt("What's the year?")
            dayofyear = typer.prompt("What's the dayofyear?")
            input_values = {"product": str(product),
                            "year": str(year),
                            "dayofyear": str(dayofyear)}
        elif req_value == "file":
            product = typer.prompt("What's the product you are looking for?")
            year = typer.prompt("What's the year?")
            dayofyear = typer.prompt("What's the dayofyear?")
            hour = typer.prompt("What's the hour?")
            input_values = {"product": str(product),
                            "year": str(year),
                            "dayofyear": str(dayofyear),
                            "hour": str(hour)}
    
        data = {
                    "table_name": table_name,
                    "req_value": req_value,
                    "input_values": input_values
                }
        
            # TESTING
            # st.write(f'access_token {st.session_state.access_token}')
            # st.write(data)
            # HANDLING 403 EXCEPTION, DUE TO 5 MIN LOGIN EXPIRATION
        try:
            response = requests.get(url = 'http://localhost:8000/field_selection', json=data, headers={'Authorization':  f'Bearer {access_token}'})
            response.raise_for_status()
            # TEST
            typer.echo(response.json())
            # st.write(response.raise_for_status())
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                typer.echo("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                typer.echo("Forbidden: You do not have permission to access this resource - Sign Back In!")
            else:
                typer.echo(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            typer.echo(f"An error occurred: {err}")

class Plans(str, Enum):
    free = "free"
    gold = "gold"
    platinium = "platinium"
 
@app.command()
def user_register(ctx: typer.Context, first_name, last_name, subscription_tier: Plans, is_admin):

    url = "http://localhost:8000"
    access_token = ""
    post = "/user/register"
    url_call = url + post

    if subscription_tier == "free":
        subscription_tier = "Free-10 Requests/hour"
    if subscription_tier == "gold":
        subscription_tier = "Gold-15 Requests/hour"
    if subscription_tier == "platinium":
        subscription_tier = "Platinum-20 Requests/hour"
    data = {
    "first_name": first_name,
    "last_name": last_name,
    "email": ctx.obj.email,
    "password": ctx.obj.password,
    "subscription_tier": str(subscription_tier),
    "is_admin": is_admin
    } 

    response = requests.post(url_call, json=data)

    if response.status_code == 405:
        typer.echo(response.json())  
    else:
        typer.echo("\nUser Created")
        res = response.json()
    
@app.command()
def s3_bucket(ctx: typer.Context,search_method, src_bucket, dest_bucket, dest_folder, prefix, file_name):
    
    logged_in = False
    url = "http://localhost:8000"
    access_token = ""
    post = "/user/login"
    url_call = url + post
    body = {
    "email": ctx.obj.email,
    "password": ctx.obj.password
    }

    response = requests.post(url_call, json=body)

    if response.status_code == 405:
        typer.echo(response.json())  
    else:
        typer.echo("Login Successfull")
        res = response.json()
        logged_in = True
        access_token = access_token + res["access_token"]
        typer.echo(f"Access Token is {access_token}")

    if logged_in:

        data = {
        "search_method": search_method,
        "src_bucket": src_bucket,
        "dest_bucket": dest_bucket,
        "dest_folder": dest_folder,
        "prefix": prefix,
        "file_name": file_name
        }

        try:
            response = requests.post(url = 'http://localhost:8000/s3_transfer', json=data, headers={'Authorization':  f'Bearer {access_token}'})
            response.raise_for_status()
            # TEST
            typer.echo(response.json())
            # st.write(response.raise_for_status())
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                typer.echo("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                typer.echo("Forbidden: You do not have permission to access this resource - Sign Back In!")
            else:
                typer.echo(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            typer.echo(f"An error occurred: {err}")

@app.command()
def lat_long(ctx: typer.Context):
    logged_in = False
    url = "http://localhost:8000"
    access_token = ""
    post = "/user/login"
    url_call = url + post
    body = {
    "email": ctx.obj.email,
    "password": ctx.obj.password
    }

    response = requests.post(url_call, json=body)

    if response.status_code == 405:
        typer.echo(response.json())  
    else:
        typer.echo("Login Successfull")
        res = response.json()
        logged_in = True
        access_token = access_token + res["access_token"]
        typer.echo(f"Access Token is {access_token}")

    if logged_in:

        try:
            response = requests.get(url = 'http://localhost:8000/latlong', headers={'Authorization':  f'Bearer {access_token}'})
            response.raise_for_status()
            # TEST
            typer.echo(response.json())
            # st.write(response.raise_for_status())
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                typer.echo("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                typer.echo("Forbidden: You do not have permission to access this resource - Sign Back In!")
            else:
                typer.echo(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            typer.echo(f"An error occurred: {err}")


@app.callback()
def common(ctx: typer.Context,
           email: str = typer.Option(..., envvar='APP_USERNAME', help='Username'),
           password: str = typer.Option(..., envvar='APP_PASSWORD', help='Password')):
    """Common Entry Point"""
    ctx.obj = Common(email, password)


if __name__ == "__main__":
    app()
