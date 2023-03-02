import streamlit as st
import requests
import json
from streamlit_extras.switch_page_button import switch_page
from Util.DbUtil import *
from datetime import datetime

#########################################
# Pages:
st.set_page_config(
    page_title="Register",
    page_icon="👋",
)

if 'first_name' not in st.session_state:
    st.session_state.first_name = ''

if 'last_name' not in st.session_state:
    st.session_state.last_name = ''

if 'email' not in st.session_state:
    st.session_state.email = ''

if 'password' not in st.session_state:
    st.session_state.password = ''

if 'access_token' not in st.session_state:
    st.session_state.access_token = ''

if 'register_disabled' not in st.session_state:
    st.session_state.register_disabled = False

if 'login_disabled' not in st.session_state:
    st.session_state.login_disabled = False

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
if 'logout_disabled' not in st.session_state:
    st.session_state.logged_in = True

if 'api_calls' not in st.session_state:
    st.session_state.api_calls = -100

########################################################################################################################

util = DbUtil("metadata.db")

########################################################################################################################

first_name = st.text_input("First Name", st.session_state.first_name, placeholder='First Name')
last_name = st.text_input("Last Name", st.session_state.last_name, placeholder='Last Name')
email = st.text_input("Email", st.session_state.email, placeholder='Email')
password = st.text_input("Password", st.session_state.password, placeholder='Password', type='password')
subscription_tier = st.selectbox('What subscription do you want to sign up for?',
                                 ('Free-10 Requests/hour', 'Gold-15 Requests/hour', 'Platinum-20 Requests/hour'))
is_admin = st.checkbox('Admin?')
register_submit = st.button('Register', disabled=st.session_state.logged_in)

if register_submit:
    st.session_state.first_name = first_name
    st.session_state.last_name = last_name
    st.session_state.email = email
    st.session_state.password = password
    st.session_state.subscription_tier = subscription_tier.split('-')[0]
    register_user = {
        'first_name': st.session_state.first_name,
        'last_name': st.session_state.last_name,
        'email': st.session_state.email,
        'password': st.session_state.password,
        'subscription_tier': st.session_state.subscription_tier,
        'is_admin': 1 if is_admin else 0
    }
    res = requests.post(url='http://backend:8000/user/register', data=json.dumps(register_user))

    # TRACKING APIS
    # Insert into USER_API for Logging
    list_of_tuples = [(st.session_state.email, 
                       'Register', 
                       'POST', 
                       f"""{json.dumps(register_user)}""", 
                       res.status_code, 
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]
    # util.insert('user_api',  ['email', 'api', 'api_type', 'request_body', 'request_status', 'time_of_request'], list_of_tuples)



    if res and res.status_code == 200:

        st.session_state.access_token = res.json()['access_token']
        st.session_state.register_disabled = True
        st.session_state.logged_in = True
        st.session_state.logout_disabled = False

        res2 = requests.get(url='http://backend:8000/user/status',
                            params={'email': st.session_state.email,
                                    'subscription_tier': st.session_state.subscription_tier},
                            headers={'Authorization': f'Bearer {st.session_state.access_token}'})

        st.session_state.api_calls = res2.json().get('API Calls Remaining')

        switch_page('sevirdatafetcher')
    elif (res.status_code == 409):
        error = "<p style='font-family:sans-serif; color:Red; font-size: 20px;'>Error: User already exists!</p>"
        st.markdown(error, unsafe_allow_html=True)
    else:
        error = "<p style='font-family:sans-serif; color:Red; font-size: 20px;'>Error: User registration failed!</p>"
        st.markdown(error, unsafe_allow_html=True)


with st.sidebar:
    if st.session_state and st.session_state.logged_in and st.session_state.email:
        st.write(f'Current User: {st.session_state.email}')
        st.write(f'Subscription Tier: {st.session_state.subscription_tier}')
        st.write(f'Remaining API Calls: {st.session_state.api_calls}')
    else:
        st.write('Current User: Not Logged In')




