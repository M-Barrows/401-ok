import streamlit as st
from tools.globals import MAX_HSA, MAX_401K, MAX_ROTH_IRA
# from tools.helper_funcs import calc_401k_match
import yaml
import time
def update_config_from_file():
    # Load the YAML data
    if st.session_state['config_file'] is not None:
        file_content = st.session_state['config_file'].getvalue().decode('utf-8')
        data = yaml.safe_load(file_content)
        st.session_state.hsa = data.get('hsa',st.session_state.hsa)
        st.session_state.hsa_match = data.get('hsa_match',0)
        st.session_state.roth_ira = data.get('roth_ira',0)
        st.session_state.trad_401k_rate = data.get('trad_401k_rate',0)
        st.session_state.roth_401k_rate = data.get('roth_401k_rate',0)
        st.session_state.salary = data.get('salary',100)
        st.session_state.min_net_pay = data.get('min_net_pay',0)
        st.session_state.misc_pre_tax_deductions = data.get('misc_pre_tax_deductions',0)
        st.session_state.misc_post_tax_deductions = data.get('misc_post_tax_deductions',0)
        st.session_state.brokerage = data.get('brokerage',0)
        st.session_state.state_local_tax = data.get('state_local_tax',0)
        st.session_state.children = data.get('children',0)
        st.session_state.pay_periods = data.get('pay_periods',0)
        st.session_state.years_to_retirement = data.get('years_to_retirement',25)
        st.session_state.roth_ira_start_balance =data.get('roth_ira_start_balance',0)
        st.session_state.roth_ira_expected_return =data.get('roth_ira_expected_return',0)
        st.session_state.hsa_start_balance =data.get('hsa_start_balance',0)
        st.session_state.hsa_expected_return =data.get('hsa_expected_return',0)
        st.session_state.roth_401k_start_balance =data.get('roth_401k_start_balance',0)
        st.session_state.roth_401k_expected_return =data.get('roth_401k_expected_return',0)
        st.session_state.trad_401k_start_balance =data.get('trad_401k_start_balance',0)
        st.session_state.trad_401k_expected_return =data.get('trad_401k_expected_return',0)
        st.session_state.edu_529_start_balance =data.get('edu_529_start_balance',0)
        st.session_state.edu_529_expected_return =data.get('edu_529_expected_return',0)
        st.session_state.brokerage_start_balance =data.get('brokerage_start_balance',0)
        st.session_state.brokerage_expected_return =data.get('brokerage_expected_return',0)

def settings_container():
    file_upload_help = f"""
        Please upload a yaml file with the any of the folowing parameters to auto-apply settings. You can copy this and paste it in the file to get a head start.

        > ⚠️For now, this only works on the first time you upload a file. This is a known bug. 
        ```yaml
        hsa: {st.session_state.get('hsa',0)}      # int annual amount
        hsa_match: {st.session_state.get('hsa_match',0)} # int annual amount
        roth_ira: {st.session_state.get('roth_ira',0)} # int annual amount
        trad_401k_rate: {st.session_state.get('trad_401k_rate',0)} # int percent (eg. 15)
        roth_401k_rate: {st.session_state.get('roth_401k_rate',0)} # int percent (eg. 10)
        salary: {st.session_state.get('salary',0)} # int annual amount
        min_net_pay: {st.session_state.get('min_net_pay',0)} # int monthly amount
        misc_pre_tax_deductions: {st.session_state.get('misc_pre_tax_deductions',0)} # int annual amount
        misc_post_tax_deductions: {st.session_state.get('misc_post_tax_deductions',0)} # int annual amount
        brokerage: {st.session_state.get('brokerage',0)} # int annual amount
        state_local_tax: {st.session_state.get('state_local_tax',0)} # float percent (eg. 4.5)
        children: {st.session_state.get('children',0)} # int
        pay_periods: {st.session_state.get('pay_periods',0)} # int
        years_to_retirement: {st.session_state.get('years_to_retirement',0)} # int
        ```
        """
    max401k_perc = int((MAX_401K*100)/(st.session_state['salary']*100)*100)
   
    errors = st.container()
    settings_container = st.expander("🔧 Settings",expanded=True)

    with settings_container:
        c_salary, c_pre_tax, c_after_tax, c_misc, c_config = st.tabs(["Salary","Pre-Tax","After Tax","Misc","Config"])

    with c_config:
        c_up_config, c_down_config = st.columns([2,1])

    with c_up_config:
        config_file = st.file_uploader("Upload Config",type=['yaml','yml'],help=file_upload_help,key='config_file',on_change=update_config_from_file)


    with c_salary:
        salary = st.number_input("Annual Salary",min_value=100,step=100, key='salary')
        pay_periods = st.number_input("Pay Periods Per Year",1,52, value=26,key="pay_periods")
        bonus = st.number_input("Annual Bonus %",0.0,15.0, value=7.5, key='bonus')
        min_net_pay = st.number_input("Minimum Allowed Net Monthly Pay",0, key='min_net_pay')
        st.session_state['bonus_amt'] = bonus/100*salary
        st.session_state['total_salary'] = salary + st.session_state['bonus_amt']

    with c_pre_tax: 
        trad_401k_rate = st.slider("401k Savings Rate", 0, max401k_perc ,key="trad_401k_rate")
        st.number_input("401k Match Rate",key="trad_401k_match_rate")
        hsa = st.number_input("Annual HSA contributions", 0,MAX_HSA,key='hsa')
        hsa_match = st.number_input("Annual HSA employer match", 0,MAX_HSA,value= 1_000,key='hsa_match')
        if (hsa + hsa_match) > MAX_HSA:
            with errors:
                st.error("HSA contributions exceed allowed maximum")
    
    with c_after_tax: 
        roth_401k_rate = st.slider("Roth 401k Savings Rate", 0,max401k_perc,key='roth_401k_rate')
        if ((trad_401k_rate + roth_401k_rate)/100) * salary > MAX_401K:
            with errors:
                st.error("401k contributions exceed allowed maximum")
        roth_ira = st.number_input("Annual Roth IRA Contributions", 0, MAX_ROTH_IRA,key='roth_ira')
        brokerage = st.number_input("After Tax Brokerage Contributions", 0,key='brokerage')
        edu_529 = st.number_input("Annual 529 Savings", 0,value=3_600,key='edu_529')

    with c_misc: 
        children = st.number_input("Number of Children",0,10,value=0,key="children")
        donations = st.number_input("Annual Charitable Donations", 0, value=1_700,key='donations')
        misc_pre_tax_deductions = st.number_input("Pre Tax Payroll Deductions", 0,key='misc_pre_tax_deductions',help="Things like healthcare premiums. This should exclude any retirement contributions handled elsewhere in this tool")
        misc_post_tax_deductions = st.number_input("Post Tax Payroll Deductions", 0,key='misc_post_tax_deductions',help="Things like insurance deductions. This should exclude any retirement contributions handled elsewhere in this tool")
        state_local_income_tax = st.number_input("State and local income tax %",1.,50.0,key='state_local_tax')

    with c_down_config:
        try:
            config_dict = {
                'hsa':st.session_state.hsa,
                'hsa_match':st.session_state.hsa_match,
                'roth_ira':st.session_state.roth_ira,
                'trad_401k_rate':st.session_state.trad_401k_rate,
                'roth_401k_rate':st.session_state.roth_401k_rate,
                'salary':st.session_state.salary,
                'min_net_pay':st.session_state.min_net_pay,
                'misc_pre_tax_deductions':st.session_state.misc_pre_tax_deductions,
                'misc_post_tax_deductions':st.session_state.misc_post_tax_deductions,
                'brokerage':st.session_state.brokerage,
                'state_local_tax':st.session_state.state_local_tax,
                'children':st.session_state.children,
                'pay_periods':st.session_state.pay_periods,
                'years_to_retirement':st.session_state.years_to_retirement,
                'roth_ira_start_balance':st.session_state.roth_ira_start_balance,
                'roth_ira_expected_return':st.session_state.roth_ira_expected_return,
                'hsa_start_balance':st.session_state.hsa_start_balance,
                'hsa_expected_return':st.session_state.hsa_expected_return,
                'roth_401k_start_balance':st.session_state.roth_401k_start_balance,
                'roth_401k_expected_return':st.session_state.roth_401k_expected_return,
                'trad_401k_start_balance':st.session_state.trad_401k_start_balance,
                'trad_401k_expected_return':st.session_state.trad_401k_expected_return,
                'edu_529_start_balance':st.session_state.edu_529_start_balance,
                'edu_529_expected_return':st.session_state.edu_529_expected_return,
                'brokerage_start_balance':st.session_state.brokerage_start_balance,
            }

            config_file = st.download_button("Download Config",icon="💾", data=yaml.dump(config_dict), file_name="401-ok-config.yaml",mime="text/plain",key='config_obj')
        except: 
            st.exception("Config could not be downloaded")
        finally:
            if config_file:
                time.sleep(5)
                st.toast("Your config has been saved",icon="💾",duration=10)

