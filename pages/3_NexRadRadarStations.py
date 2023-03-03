import folium 
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from Util.DbUtil import DbUtil
import requests
from datetime import datetime


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

st.title("NexRad Radar Stations")
if not st.session_state.email == "" and st.session_state.api_calls > 0:
    util = DbUtil('metadata.db')
    conn = util.conn

    res = requests.get(url='http://backend:8000/latlong')

    # TRACKING APIS

                

    if res and res.status_code == 200:
        l = eval(res.json()['data'])
        data = pd.DataFrame(l, columns=["station", "LAT", "LONG", "city"])
        st.subheader("The data here contains locations of current and archived radar stations. The map denotes these specified stations by a blue pin.")
        st.caption("Note: You can find information like the station name and city in which station is located by hovering over the points.")

        map_loc = data[["LAT", "LONG", "station", "city"]]

        map = folium.Map(location=[map_loc.LAT.mean(), map_loc.LONG.mean()], zoom_start=4, control_scale=True)

        # Adding the points to the map by itterating through the dataframe
        for index, location_info in map_loc.iterrows():
            folium.Marker([location_info["LAT"], location_info["LONG"]],
            popup=[location_info["LAT"], location_info["LONG"]],
            tooltip=[location_info["LAT"], location_info["LONG"], "Station: " + location_info["station"], "City: " + location_info["city"]]).add_to(map)

        st_data = st_folium(map, width=725)
        list_of_tuples = [(st.session_state.email,
                           'NEXRAD_Radar',  # api
                           'GET',  # api_type
                           f"""""",  # response_body
                           res.status_code,
                           datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # time_of_request
                           )]
        # print(list_of_tuples)
        # Insert into USER_API for Logging
        util.insert('user_api', ['email', 'api', 'api_type', 'request_body', 'request_status', 'time_of_request'],
                    list_of_tuples)
        res2 = requests.get(url='http://backend:8000/user/status', params={'email': st.session_state.email,
                                                                           'subscription_tier': st.session_state.subscription_tier},
                            headers={'Authorization': f'Bearer {st.session_state.access_token}'})

        st.session_state.api_calls = res2.json().get('API Calls Remaining')
    elif res and res.status_code == 403:
        st.session_state.logout_disabled = False
        error = """<p style="font-family:sans-serif; color:Red; font-size: 20px;">Session TimedOut, Sign Back In!</p>"""
        st.markdown(error, unsafe_allow_html=True)
    else:
        error = """<p style="font-family:sans-serif; color:Red; font-size: 20px;">Error while fetching the lat long data</p>"""
        st.markdown(error, unsafe_allow_html=True)

    util.conn.close()
else:
    st.write('Please Login!')
