import streamlit as st


accounts = [
    {'display_name': 'Roth IRA', 'session_state_key': 'roth_ira'},
    {'display_name': 'HSA', 'session_state_key': 'hsa'},
    {'display_name': 'Roth 401k', 'session_state_key': 'roth_401k'},
    {'display_name': 'Traditional 401k', 'session_state_key': 'trad_401k'},
    {'display_name': '529', 'session_state_key': 'edu_529'},
    {'display_name': 'Brokerage', 'session_state_key': 'brokerage'},
]

st.subheader(f"{st.session_state.get('primary_name', 'My')}'s Accounts")

items_per_column = len(accounts)//3 if len(accounts)%3 == 0 else (len(accounts)//3)+1

c_1, c_2, c_3 = st.columns(3)
with c_1:
    for account in accounts[:items_per_column]:
        with st.container(border=True):
            st.write(account['display_name'])
            start, rate = st.columns(2)
            with start:
                st.number_input("Current Balance", key=f"{account['session_state_key']}_start_balance")
            with rate:
                st.number_input("Expected Return (%)", key=f"{account['session_state_key']}_expected_return")
with c_2:
    for account in accounts[items_per_column:(items_per_column*2)]:
        with st.container(border=True):
            st.write(account['display_name'])
            start, rate = st.columns(2)
            with start:
                st.number_input("Current Balance", key=f"{account['session_state_key']}_start_balance")
            with rate:
                st.number_input("Expected Return (%)", key=f"{account['session_state_key']}_expected_return")
with c_3:
    for account in accounts[(items_per_column*2):]:
        with st.container(border=True):
            st.write(account['display_name'])
            start, rate = st.columns(2)
            with start:
                st.number_input("Current Balance", key=f"{account['session_state_key']}_start_balance")
            with rate:
                st.number_input("Expected Return (%)", key=f"{account['session_state_key']}_expected_return")

if st.session_state.get('spousal_enabled', False):
    spouse_name = st.session_state.get('spouse_name', 'Spouse2')
    st.divider()
    st.subheader(f"{spouse_name}'s Accounts")

    spouse_accounts = [
        {'display_name': 'Roth IRA', 'session_state_key': 'spouse_roth_ira'},
        {'display_name': 'HSA', 'session_state_key': 'spouse_hsa'},
        {'display_name': 'Roth 401k', 'session_state_key': 'spouse_roth_401k'},
        {'display_name': 'Traditional 401k', 'session_state_key': 'spouse_trad_401k'},
        {'display_name': 'Brokerage', 'session_state_key': 'spouse_brokerage'},
    ]

    sp_items = len(spouse_accounts) // 3 if len(spouse_accounts) % 3 == 0 else (len(spouse_accounts) // 3) + 1

    sc_1, sc_2, sc_3 = st.columns(3)
    with sc_1:
        for account in spouse_accounts[:sp_items]:
            with st.container(border=True):
                st.write(account['display_name'])
                start, rate = st.columns(2)
                with start:
                    st.number_input("Current Balance", key=f"{account['session_state_key']}_start_balance")
                with rate:
                    st.number_input("Expected Return (%)", key=f"{account['session_state_key']}_expected_return")
    with sc_2:
        for account in spouse_accounts[sp_items:(sp_items * 2)]:
            with st.container(border=True):
                st.write(account['display_name'])
                start, rate = st.columns(2)
                with start:
                    st.number_input("Current Balance", key=f"{account['session_state_key']}_start_balance")
                with rate:
                    st.number_input("Expected Return (%)", key=f"{account['session_state_key']}_expected_return")
    with sc_3:
        for account in spouse_accounts[(sp_items * 2):]:
            with st.container(border=True):
                st.write(account['display_name'])
                start, rate = st.columns(2)
                with start:
                    st.number_input("Current Balance", key=f"{account['session_state_key']}_start_balance")
                with rate:
                    st.number_input("Expected Return (%)", key=f"{account['session_state_key']}_expected_return")
