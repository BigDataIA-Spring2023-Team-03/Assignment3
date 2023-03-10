import streamlit as st
import requests
import json
from streamlit_extras.switch_page_button import switch_page
from Util.DbUtil import *
from datetime import datetime

#########################################
# Pages:
st.set_page_config(
    page_title="DAMG7245_Spring2023 Group 03",
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

if 'subscription_tier' not in st.session_state:
    st.session_state.subscription_tier = ''

if 'access_token' not in st.session_state:
    st.session_state.access_token = ''

if 'login_disabled' not in st.session_state:
    st.session_state.login_disabled = False

if 'logout_disabled' not in st.session_state:
    st.session_state.logout_disabled = True

if 'register_disabled' not in st.session_state:
    st.session_state.register_disabled = False

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'api_calls' not in st.session_state:
    st.session_state.api_calls = -100

########################################################################################################################

util = DbUtil("metadata.db")

########################################################################################################################

email = st.text_input("Email", st.session_state.email, placeholder='Email')
password = st.text_input("Password", st.session_state.password, placeholder='Password', type = 'password')
login_submit = st.button('Login', disabled = st.session_state.login_disabled)

if login_submit:
    st.session_state.email = email
    st.session_state.password = password
    login_user = {
        'email': st.session_state.email,
        'password': st.session_state.password
    }
    res = requests.post(url='http://backend:8000/user/login', data=json.dumps(login_user))

    # TRACKING APIS
    # Insert into USER_API for Logging
    list_of_tuples = [(st.session_state.email, 
                       'Login', 
                       'POST', 
                       f"""{json.dumps(login_user)}""", 
                       res.status_code, 
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]
    # print(list_of_tuples)
    # util.insert('user_api',  ['email', 'api', 'api_type', 'request_body', 'request_status', 'time_of_request'], [(st.session_state.email, 'Login', 'POST', f"""{json.dumps(login_user)}""", res.status_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))])
    # util.insert('user_api',  ['email', 'api', 'api_type', 'request_body', 'request_status', 'time_of_request'], list_of_tuples)

    if res and res.status_code == 200:
        # st.experimental_rerun()
        st.session_state.access_token = res.json()['access_token']
        st.session_state.login_disabled = True
        st.session_state.logged_in = True
        st.session_state.logout_disabled = False
        # Get Subscription_tier for logged in user
        query = f'''SELECT DISTINCT SUBSCRIPTION_TIER
        FROM USERS
        WHERE EMAIL = '{st.session_state.email}';'''

        st.session_state.subscription_tier = util.execute_custom_query(query)[0][0]
        res2 = requests.get(url='http://backend:8000/user/status', params={'email': st.session_state.email,
                                                                          'subscription_tier': st.session_state.subscription_tier},
                           headers={'Authorization': f'Bearer {st.session_state.access_token}'})

        st.session_state.api_calls = res2.json().get('API Calls Remaining')

        # TESTING
        # st.write(query)
        # st.write(st.session_state.subscription_tier)

        switch_page('sevirdatafetcher')

    elif res.status_code == 401 or res.status_code == 422:
        switch_page('registerpage')
    else:
        error = "<p style='font-family:sans-serif; color:Red; font-size: 20px;'>Error: User doesn't exist!</p>"
        st.markdown(error, unsafe_allow_html=True)


with st.sidebar:
    if st.session_state and st.session_state.logged_in and st.session_state.email:
        st.write(f'Current User: {st.session_state.email}')
        st.write(f'Subscription Tier: {st.session_state.subscription_tier}')
        st.write(f'Remaining API Calls: {st.session_state.api_calls}')
    else:
        st.write('Current User: Not Logged In')

    logout_submit = st.button('LogOut', disabled = st.session_state.logout_disabled)
    if logout_submit:
        for key in st.session_state.keys():
            if key == 'login_disabled' or key == 'logout_disabled' or key == 'register_disabled' or key == 'logged_in':
                st.session_state[key] = not st.session_state[key]
            elif key == 'api_calls':
                st.session_state[key] = -100
            else:
                st.session_state[key] = ''
        st.session_state.login_disabled = False
        st.experimental_rerun()




