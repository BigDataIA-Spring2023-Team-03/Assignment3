# FASTAPI Fetcher

FASTAPI Fetcher is an application that fetches GEOS-18 satellite data and NEXRAD data by making FASTAPI calls. The application is built on Streamlit, and in the backend, FAST API is used. Both the front-end and back-end are Dockerized into separate Docker containers. Users can search the data file using mainly two methods: using file name search - the file URL for S3 bucket is generated using the string filename, and using field selection - where users can select individual fields and get the file. The file can be downloaded or pushed into your S3 bucket.

## FAST API

FAST API is used for the main backend code to fetch the NEXRAD and GEOS-18 files. There are also authentication tokens generated for each user login. The API uses metadata.db database file to fetch values. A sign-in and authentication feature is added using JWT, which is also used for authentication for each user.

## AWS Logging

We have implemented AWS logging system that keeps track of all the Log information into our S3 account. The logs basically store information such as log-group-name, log-stream-name and log-events such as time, stamps, and messages.

## Streamlit

We have used Python Streamlit for the main front-end of our application. This Streamlit application is hosted on port 8501 for localhost users. The app is paginated into several pages like login where users could log in to their account, register page where new users could sign up, and two other main pages should be locked until login. These two pages or the file feature which connects to the bank and fast API and the station locations for NEXRAD.

## Great Expectation

Great expectation is a Python library that we have used for data quality testing. We have created several checkpoints to check our expectations and evaluate the data quality.

## Apache Airflow

Apache Airflow has been used in the project for some trigger-based automation tasks such as updating the metadata database file, which contains metadata for NEXRAD and GEOS18 metadata. From the S3 bucket, which are as follows: 
- GEOS18 S3 bucket - https://noaa-goes18.s3.amazonaws.com/index.html/ 
- NEXRAD S3 bucket - https://noaa-nexrad-level2.s3.amazonaws.com/index.html. 

We also use Airflow DAGs to create a great expectation report, once the data is fetched and updated to the metadata database file. 

## Docker

We have used Docker containers to containerize our application into three separate containers. Two of these containers, namely, the front-end and back-end container, can communicate with each other, which we have defined in the docker-compose.yaml file. We have also created another container for our airflow Apache DAGs, where we have used Docker storage mount to share the metadata database file.

## Installation

#### Pre-requisites
- Docker - https://docs.docker.com/engine/install/
- Docker App - https://docs.docker.com/get-docker/
- Apache Airflow -https://airflow.apache.org

1. Clone the repository: 

`git clone https://github.com/BigDataIA-Spring2023-Team-03/Assignment2.git`


2. Open the Application folder on any IDE. For this example, we will be using Visual Studio Code.

3. Open a new terminal in VSCode and type the following commands:

`docker-compose build`


4. Once the build is successful, run:

`docker-compose up`


5. For running the app locally, once the above commands are still running, go to: http://localhost:8501/

6. Here, you can register or login to the application. Once logged in, you would be redirected to the DataFetcher Page.

## Acknowledgements
The FASTAPI Fetcher was built by the BigDataIA-Spring2023-Team-03 group as part of an assignment. Special thanks to the following technologies:

- Streamlit
- FASTAPI
- Great Expectation
- Apache Airflow
- Docker
- AWS S3 Bucket



## Team Information

| NAME                      |     NUID        |
|---------------------------|-----------------|
|   Raj Mehta               |   002743076     |
|   Mani Deepak Reddy Aila  |   002728148     |
|   Jared Videlefsky        |   001966442     |
|   Rumi Jha                |   002172213     |
 

## CLAAT Link 

For Detailed documentation- [Click here](https://codelabs-preview.appspot.com/?file_id=13bISkcPZwNQ5-8rs55OgNK-DbexBzB3MhbuWXRKY9kI#7)

## Contributions

- Raj Mehta
- Mani Deepak Reddy Aila - 45%
- Jared Videlefsky
- Rumi Jha


