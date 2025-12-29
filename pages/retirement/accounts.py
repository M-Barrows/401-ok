import streamlit as st

accounts = [ 
    {
        'display_name': 'Roth IRA',
        'session_state_key':'roth_ira'
    },
    {
        'display_name': 'HSA',
        'session_state_key': 'hsa'
    },
    {
        'display_name': 'Roth 401k',
        'session_state_key': 'roth_401k'
    },
    {
        'display_name': 'Traditional 401k',
        'session_state_key': 'trad_401k'
    },
    {
        'display_name': '529',
        'session_state_key': 'edu_529'
    },
    {
        'display_name': 'Brokerage',
        'session_state_key': 'brokerage'
    },
]


items_per_column = len(accounts)//3 if len(accounts)%3 == 0 else (len(accounts)//3)+1

c_1, c_2, c_3 = st.columns(3)
with c_1:
    for account in accounts[:items_per_column]:
        account_container = st.container(border=True)
        with account_container:
            st.write(account['display_name'])
            start, rate = st.columns(2)
            with start: 
                st.number_input("Balance", key=f"{account['session_state_key']}_start_balance")
            with rate: 
                st.number_input("Rate", key=f"{account['session_state_key']}_expected_return")
with c_2: 
    for account in accounts[items_per_column:(items_per_column*2)]:
        account_container = st.container(border=True)
        with account_container:
            st.write(account['display_name'])
            start, rate = st.columns(2)
            with start: 
                st.number_input("Balance", key=f"{account['session_state_key']}_start_balance")
            with rate: 
                st.number_input("Rate", key=f"{account['session_state_key']}_expected_return")

with c_3: 
    for account in accounts[(items_per_column*2):]:
        account_container = st.container(border=True)
        with account_container:
            st.write(account['display_name'])
            start, rate = st.columns(2)
            with start: 
                st.number_input("Balance", key=f"{account['session_state_key']}_start_balance")
            with rate: 
                st.number_input("Rate", key=f"{account['session_state_key']}_expected_return")
st.session_state
