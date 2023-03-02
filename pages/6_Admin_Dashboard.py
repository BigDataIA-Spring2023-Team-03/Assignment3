import streamlit as st
import pandas as pd
from Util.DbUtil import DbUtil

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

    cursor = conn.cursor()

    cursor.execute(f"select admin from users where email = '{st.session_state.email}'")
    l = cursor.fetchall()

    if l[0][0] == 1:

        df = pd.read_sql_query('select * from user_api', conn)
        st.write(df)

        df2 = pd.read_sql_query('select email, count(email) as count from user_api group by email', conn)
        st.write(df2)

        df3 = pd.read_sql_query('select api, count(api) as count from user_api group by api', conn)
        df3 = df3.set_index('api')
        st.write(df3)
        st.bar_chart(df3)

        # write query to get total API calls for the day
        # write query to get
        df4 = pd.read_sql_query("SELECT COUNT(*) as count FROM USER_API WHERE DATETIME(time_of_request) >= datetime(strftime('%Y-%m-%d 00:00:00', 'now', '0 day'))", conn)
        st.write(df4)
        st.metric("Number of Calls made Today", df4.loc[0,'count'])

        # df5 = pd.read_sql_query("""Select case
        #             when (((SELECT COUNT(*)
        #             FROM USER_API
        #             WHERE DATETIME(time_of_request) >= datetime(strftime('%Y-%m-%d 00:00:00', 'now', '-1 day'))) - (SELECT COUNT(*)
        #             FROM USER_API
        #             WHERE DATETIME(time_of_request) >= datetime(strftime('%Y-%m-%d 00:00:00', 'now', '0 day'))))) <> 0
        #             THEN ((SELECT COUNT(*)
        #             FROM USER_API
        #             WHERE DATETIME(time_of_request) >= datetime(strftime('%Y-%m-%d 00:00:00', 'now', '0 day')))/((SELECT COUNT(*)
        #             FROM USER_API
        #             WHERE DATETIME(time_of_request) >= datetime(strftime('%Y-%m-%d 00:00:00', 'now', '-1 day'))) - (SELECT COUNT(*)
        #             FROM USER_API
        #             WHERE DATETIME(time_of_request) >= datetime(strftime('%Y-%m-%d 00:00:00', 'now', '0 day'))))) * 100
        #             else NULL
        #             end
        #              as percentage_increase""", conn)
        #
        # if df5.loc[0,'percentage_increase'] is None:
        #     delta = None
        # else:
        #     delta = str(df5.loc[0,'percentage_increase'])
        #
        # st.metric("Number of Calls made Today", df4.loc[0,'count'], delta)
    else:
        st.write('Only admin has access to this!')

    util.conn.close()
else:
    st.write('Please Login!')