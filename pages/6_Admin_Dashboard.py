import streamlit as st
import pandas as pd
from Util.DbUtil import DbUtil
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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
########################################################################################################################

util = DbUtil("metadata.db")

########################################################################################################################

st.title("App Summary Dashboard")

if not st.session_state.email == "" and st.session_state.api_calls > 0:

    conn = util.conn

    cursor = conn.cursor()

    cursor.execute(f"select admin from users where email = '{st.session_state.email}'")
    l = cursor.fetchall()

    if l[0][0] == 1:
        ######################################################################################################
        # Summary
        # TODO: Make Interactive using timeframe, change days
        st.header('Summary')

        query = f"""
        select 'Alltime' timeframe,
                round(julianday('now') - julianday(min(time_of_request))) days,
                count(distinct email) total_users,
                count(*) total_requests,
                count(case when request_status = 200 then 1 end) total_successful_requests,
                count(case when request_status != 200 then 1 end) total_erroneous_requests
        from user_api 
        union
        select 'Last_Week' timeframe,
                7 days,
                count(distinct email) total_users,
                count(*) total_requests,
                count(case when request_status = 200 then 1 end) total_successful_requests,
                count(case when request_status != 200 then 1 end) total_erroneous_requests
        from user_api
        where DATETIME(TIME_OF_REQUEST) >= DATETIME('{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', '-7 day')
        """
        df = pd.read_sql_query(query, conn)

        # Add in Averages
        df = df.astype({'days':'int'})  
        df['average_requests'] = df['total_requests'] / df['days']

        st.write(df)

        ######################################################################################################
        # User Requests Over Time
        st.header('User Request Over Time')
        # Dropdown list of users
        query = """select distinct email from user_api order by email"""
        df = pd.read_sql_query(query, conn)
        user_list = tuple(list(df['email']))
        # st.write(user_list)

        select_user = st.selectbox('Which user do you want a request vs. time history for?',
                                    user_list)
        st.write('You selected:', select_user)

        query = f"""
        select email, date(time_of_request) date, count(*)  total_requests
        from user_api 
        where email = '{select_user}'
        group by email, date
        """
        df = pd.read_sql_query(query, conn)
        # TESTING
        # st.write(df.head())
        # st.write(df.dtypes)

        fig = plt.figure(figsize=(10, 4))
        sns.lineplot(x='date', y='total_requests', hue='email', 
                    data=df,
                    markers=True).set(ylim=(0))
        st.pyplot(fig)


        ######################################################################################################
        # Total Requests Over Time
        # TODO: turn into bar graph where you can see the breakdown of success/failure request status
        st.header('User Request Over Time')

        query = f"""
        select date(time_of_request) date, 
                count(distinct email) total_users,
                count(*) total_requests
        from user_api 
        group by date
        """
        df = pd.read_sql_query(query, conn)
        # TESTING
        # st.write(df.head())
        # st.write(df.dtypes)

        fig = plt.figure(figsize=(10, 4))
        g = sns.lineplot(x=df.date, y=df.total_requests, color="g")
        sns.lineplot(x=df.date, y=df.total_users, color="b", ax=g.axes.twinx())
        g.legend(handles=[Line2D([], [], marker='_', color="g", label='total_requests'), 
                        Line2D([], [], marker='_', color="b", label='total_users')])

        st.pyplot(fig)


        ######################################################################################################
        # Running Totals Over Time
        # TODO: Add in user growth
        st.header('Running Totals Over Time')

        query = f"""
        with totals as (
        select date(time_of_request) date, 
                -- count(distinct email) total_users,
                count(*) total_requests
        from user_api 
        group by date
        order by date
        )
        select date, 
                -- total_users,
                sum(total_requests) over (rows unbounded preceding) total_requests
        from totals
        """
        df = pd.read_sql_query(query, conn)
        # TESTING
        # st.write(df.head())
        # st.write(df.dtypes)

        fig = plt.figure(figsize=(10, 4))
        sns.lineplot(x='date', y='total_requests', 
                    data=df,
                    markers=True).set(ylim=(0))
        st.pyplot(fig)


        ######################################################################################################
        # Details
        st.header('Details')
        # Recent API Calls
        df = pd.read_sql_query('select * from user_api order by time_of_request desc', conn).head(100)
        st.write('100 Most Recent API Calls:')
        st.write(df)

        # # Recent API Calls
        # df = pd.read_sql_query('select * from user_api order by time_of_request desc', conn).head(100)
        # st.write('100 Most Recent API Calls:')
        # st.write(df)

        # df2 = pd.read_sql_query('select email, count(email) as count from user_api group by email', conn)
        # st.write(df2)

        # df3 = pd.read_sql_query('select api, count(api) as count from user_api group by api', conn)
        # df3 = df3.set_index('api')
        # st.write(df3)
        # st.bar_chart(df3)

        # # write query to get total API calls for the day
        # # write query to get
        # df4 = pd.read_sql_query("SELECT COUNT(*) as count FROM USER_API WHERE DATETIME(time_of_request) >= datetime(strftime('%Y-%m-%d 00:00:00', 'now', '0 day'))", conn)
        # st.write(df4)
        # st.metric("Number of Calls made Today", df4.loc[0,'count'])

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