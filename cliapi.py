import typer
from dotenv import load_dotenv
from dataclasses import dataclass
import requests
import json
load_dotenv()

app = typer.Typer(add_completion=False)


@dataclass
class Common:
    email: str
    password: str


@app.command()
def feild_selection(ctx: typer.Context, table_name: str, req_value: str, input_values):

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


        data = {
                    "table_name": table_name,
                    "req_value": req_value,
                    "input_values": {"product": 'ABI-L1b-RadC'}
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

 
@app.command()
def user_register(ctx: typer.Context, first_name, last_name):

    url = "http://localhost:8000"
    access_token = ""
    post = "/user/register"
    url_call = url + post

    data = {
    "first_name": first_name,
    "last_name": last_name,
    "email": ctx.obj.email,
    "password": ctx.obj.password
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
