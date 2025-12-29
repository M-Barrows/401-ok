import streamlit as st

defaults = { 
    'hsa':0,
    'hsa_match': 0,
    'roth_ira': 0,
    'trad_401k_rate': 15,
    'trad_401k_match_rate': 3,
    'roth_401k_rate': 0,
    'edu_529': 0,
    'salary':60_000,
    'min_net_pay': 3_500,
    'misc_pre_tax_deductions':1_000,
    'misc_post_tax_deductions':1_000,
    'brokerage':0,
    'state_local_tax':5.0,
    'taxable_income':0,
    'children':0,
    'years_to_retirement':25,
    'roth_ira_start_balance':0,
    'roth_ira_expected_return':8,
    'hsa_start_balance':0,
    'hsa_expected_return':8,
    'roth_401k_start_balance':0,
    'roth_401k_expected_return':8,
    'trad_401k_start_balance':0,
    'trad_401k_expected_return':8,
    'edu_529_start_balance':0,
    'edu_529_expected_return':8,
    'brokerage_start_balance':0,
    'brokerage_expected_return':8,
}
def init_session_data():

    # if 'config_dict' not in st.session_state:
    #     st.session_state['config_dict'] = dict()
    for k,v in defaults.items():
      if k not in st.session_state:
            st.session_state[k] = v

# def update_config_dict():
#     for k,v in defaults.items():
#         st.session_state['config_dict'][k] = st.session_state.get(k,v)

__all__ = ['init_session_data','defaults']
