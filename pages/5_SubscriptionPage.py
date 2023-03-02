import streamlit as st
import pandas as pd
from Util.DbUtil import *
from datetime import datetime
import requests


if 'email' not in st.session_state:
    st.session_state.email = ''

if 'subscription_tier' not in st.session_state:
    st.session_state.subscription_tier = ''

if 'logout_disabled' not in st.session_state:
    st.session_state.logout_disabled = True

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

###################################################################################
# Side Bar
with st.sidebar:
    user = "Not Logged In" if st.session_state.email == "" else st.session_state.email
    st.write(f'Current User: {user}')
    st.write(f'Subscription Tier: {st.session_state.subscription_tier}')
    st.write(f'Remaining API Calls: {st.session_state.api_calls}')
    logout_submit = st.button('LogOut', disabled=st.session_state.logout_disabled)
    if logout_submit:
        for key in st.session_state.keys():
            if key == 'login_disabled' or key == 'logout_disabled' or key == 'register_disabled' or key == 'logged_in':
                st.session_state[key] = not st.session_state[key]
            elif key == 'api_calls':
                st.session_state[key] = -100
            else:
                st.session_state[key] = ''
        st.session_state.login_disabled = False
        st.session_state.register_disabled = False
        st.experimental_rerun()
###################################################################################
########################################################################################################################

util = DbUtil("metadata.db")

########################################################################################################################


st.title("Subscription Information")
if not st.session_state.email == "" and st.session_state.api_calls > 0:
    conn = util.conn

    # Check API Requests Remaining
    if st.button('Check API Requests Remaining'):
        data = {
                'email': st.session_state.email,
                'subscription_tier': st.session_state.subscription_tier
                }
        res = requests.get(url='http://backend:8000/user/status', params= {'email': st.session_state.email, 'subscription_tier': st.session_state.subscription_tier}, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
        
        if res and res.status_code == 200:
            api_calls_remaining = res.json().get('API Calls Remaining')
            st.write(f'You currently have {api_calls_remaining} API calls remaining.')
            st.write('Use the Upgrade Subscription button below to unlock more API Calls!')

        elif res and res.status_code == 403:
            st.session_state.logout_disabled = False
            error = """<p style="font-family:sans-serif; color:Red; font-size: 20px;">Session TimedOut, Sign Back In!</p>"""
            st.markdown(error, unsafe_allow_html=True)
        else:
            error = """<p style="font-family:sans-serif; color:Red; font-size: 20px;">Error while fetching API Requests Remaining</p>"""
            st.markdown(error, unsafe_allow_html=True)

    # Upgrade Subscription
    subscription_tier = st.selectbox('What subscription do you want to sign up for?',
                                ('', 'Free-10 Requests/hour', 'Gold-15 Requests/hour', 'Platinum-20 Requests/hour'))
    subscription_tier = subscription_tier.split('-')[0] # Just grabs the tier

    
    if st.button('Upgrade Subscription'):
        # TESTING
        # st.write(subscription_tier)

        if subscription_tier != '':
            if subscription_tier != st.session_state.subscription_tier:
                data = {
                    'email': st.session_state.email,
                    'subscription_tier': subscription_tier
                }
                res = requests.post(url='http://backend:8000/user/subscription_upgrade', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
                
                # TRACKING APIS
                # Insert into USER_API for Logging
                list_of_tuples = [(st.session_state.email, 
                                'Subscription_Upgrade', 
                                'POST', 
                                f"""{data}""", 
                                res.status_code, 
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]
                # print(list_of_tuples)
                # util.insert('user_api',  ['email', 'api', 'api_type', 'request_body', 'request_status', 'time_of_request'], [(st.session_state.email, 'Login', 'POST', f"""{json.dumps(login_user)}""", res.status_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))])
                util.insert('user_api',  ['email', 'api', 'api_type', 'request_body', 'request_status', 'time_of_request'], list_of_tuples)
                res2 = requests.get(url='http://backend:8000/user/status',
                                    params={'email': st.session_state.email,
                                            'subscription_tier': st.session_state.subscription_tier},
                                    headers={'Authorization': f'Bearer {st.session_state.access_token}'})

                st.session_state.api_calls = res2.json().get('API Calls Remaining')

                if res and res.status_code == 200:
                    # If it works update the session state
                    st.session_state.subscription_tier = subscription_tier

                    st.write(f'''Your Subscription Tier has been updated to {st.session_state.subscription_tier}!''') # TODO #, you now have {subscription_tier.split('-')[1]} API Calls/hour!''')
                
                elif res and res.status_code == 403:
                    st.session_state.logout_disabled = False
                    error = """<p style="font-family:sans-serif; color:Red; font-size: 20px;">Session TimedOut, Sign Back In!</p>"""
                    st.markdown(error, unsafe_allow_html=True)
                else:
                    error = """<p style="font-family:sans-serif; color:Red; font-size: 20px;">Error while upgrading Subscription!</p>"""
                    st.markdown(error, unsafe_allow_html=True)
            # Can't select current tier
            else: # subscription_tier == st.session_state.subscription_tier:
                error = """<p style="font-family:sans-serif; color:Red; font-size: 20px;">Can't select current tier!</p>"""
                st.markdown(error, unsafe_allow_html=True)


    util.conn.close()
else:
    st.write('Please Login!')
