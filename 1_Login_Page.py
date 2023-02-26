import streamlit as st
import requests
import json
from streamlit_extras.switch_page_button import switch_page

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
    if res and res.status_code == 200:
        # st.experimental_rerun()
        st.session_state.access_token = res.json()['access_token']
        st.session_state.login_disabled = True
        st.session_state.logged_in = True
        st.session_state.logout_disabled = False
        switch_page('sevirdatafetcher')

    elif res.status_code == 401 or res.status_code == 422:
        switch_page('registerpage')
    else:
        error = "<p style='font-family:sans-serif; color:Red; font-size: 20px;'>Error: User doesn't exist!</p>"
        st.markdown(error, unsafe_allow_html=True)


with st.sidebar:
    if st.session_state and st.session_state.logged_in and st.session_state.email:
        st.write(f'Current User: {st.session_state.email}')
    else:
        st.write('Current User: Not Logged In')

    logout_submit = st.button('LogOut', disabled = st.session_state.logout_disabled)
    if logout_submit:
        for key in st.session_state.keys():
            if key == 'login_disabled' or key == 'logout_disabled' or key == 'register_disabled' or key == 'logged_in':
                st.session_state[key] = not st.session_state[key]
            else:
                st.session_state[key] = ''
        st.session_state.login_disabled = False
        st.experimental_rerun()




