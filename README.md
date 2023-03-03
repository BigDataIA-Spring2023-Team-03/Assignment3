## FAST API

FASTAPI is used in the backend code to limit the user API request- monitor their subscribed plan usage and suggest an upgradation plan. There are also authentication tokens generated for each user login. The API uses the metadata.db database file to fetch values. A sign-in and authentication feature is added using JWT, which is also used for authentication for each user.

## Streamlit

We have used Python Streamlit for the main front end of our application. This Streamlit application is hosted on port 8501 for local-host users. The app is paginated into several pages like login where users can log in to their account, register page where new users can sign up, and two other main pages that should be locked until login. These two pages or the file feature connect to the bank and fast API and the station locations for NEXRAD.

Apart from that it also monitors user activities like the number of API call requests by a user, the number of successful and unsuccessful call requests, etc

## CLI

Here we have used the Typer library to define a command-line interface application that interacts with an API for data manipulation. Also, we have used the Poetry tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you. Poetry offers a lock file to ensure repeatable installs and can build your project for distribution.

## Docker

We have used Docker containers to containerize our application into three separate containers. Two of these containers, namely, the front-end and back-end container, can communicate with each other, which we have defined in the docker-compose.yaml file. 

## CLI

We have used typer-cli module to build CLI for our FAST Api. Typer CLI is a command line application to run simple programs created with Typer, with completion in your terminal 🚀.

You use Typer CLI in your terminal, to run your scripts as an alternative to calling python directly

Here are some Basic Commands for our cliapi.py 

 Usage: cliapi.py [OPTIONS] COMMAND [ARGS]...                                                                                                                      
 Common Entry Point

╭─ Options ──────────────────────────────────────────────────────────────────────────────╮

│ *  --email           TEXT  Username [env var: APP_USERNAME] [default: None] [required] |                                                                                                                                              │

│ *  --password        TEXT  Password [env var: APP_PASSWORD] [default: None] [required] |                                                                                                                                              │

│    --help                  Show this message and exit.                                 |                                                                                                                                              │

╰────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Commands────────────╮

│ feild-selection                                                                                                                                                                │

│ lat-long                                                                                                                                                                        │

│ s3-bucket                                                                                                                                                                      │

│ user-register                                                                                                                                                                  │

╰─────────────────────╯

Here are list of some basic command examples:
User Registration
```sh
python cliapi.py --email your_email --password password user-register First_name Last_name Tier Admin
```

Field Selection
```sh
python cliapi.py --email your_email --password password feild-selection table_name req_values
```

Example:
<img width="1194" alt="feild-selection-example" src="https://user-images.githubusercontent.com/61338379/222836160-3f8d046d-58b7-4919-8da6-391e01b35860.png">


CLI Help can be accessed in following way:

<img width="633" alt="cli_help" src="https://user-images.githubusercontent.com/61338379/222836493-7f96d099-d8ca-45be-983b-3c8e421ec5ea.png">


Command Help can be accessed in following way:

<img width="985" alt="command_help" src="https://user-images.githubusercontent.com/61338379/222836648-579869aa-f19a-400b-8a3c-18f689b260c3.png">



## Wheels

We have used wheels as a pre-built binary package format for Python modules and libraries to access the APIs. They are designed to make it easier to install and manage Python packages, by providing a convenient, single-file format that can be downloaded and installed without the need to compile the package from source code

#### Pre-requisites


1. Clone the repository: 

```sh
git clone https://github.com/BigDataIA-Spring2023-Team-03/Assignment3.git
```


2. Open the Application folder on any IDE. For this example, we will be using Visual Studio Code.

3. Open a new terminal in VSCode and type the following commands:
```sh
docker-compose build
```


4. Once the build is successful, run:

```sh
docker-compose up
```


5. For running the app locally, once the above commands are still running, go to: http://52.201.212.226:8501/

6. Here, you can register or login to the application. Once logged in, you would be redirected to the DataFetcher Page.

## Acknowledgements
The CLI was built by the BigDataIA-Spring2023-Team-03 group as part of this assignment. Special thanks to the following technologies and Python Libraries:

- FASTAPI
- Streamlit
- Typer
- Poetry
- Wheel



## Team Information

| NAME                      |     NUID        |
|---------------------------|-----------------|
|   Raj Mehta               |   002743076     |
|   Mani Deepak Reddy Aila  |   002728148     |
|   Jared Videlefsky        |   001966442     |
|   Rumi Jha                |   002172213     |
 

## CLAAT Link 

For Detailed documentation- [Click here](https://codelabs-preview.appspot.com/?file_id=13Lu_KA8h4WPHTBIyg0DzN-B6zXmzNwb8xc2egh3dOjk)

## Live Application Link

[Application Link](http://52.201.212.226:8501/)

## Contributions

- Raj Mehta - 25%
- Mani Deepak Reddy Aila - 25%
- Jared Videlefsky - 25%
- Rumi Jha - 25%


