import streamlit as st
import pandas as pd
import yaml
from src.helper_funcs import calc_401k_match, calculate_tax, calculate_taxable_income,compute_net_monthly, optimize_for_foo,calculate_total_savings_dollars, calculate_total_takehome_paycheck
from src.globals import MAX_401K,MAX_ROTH_IRA,MAX_HSA,CHILD_TAX_CREDIT,BRACKETS

st.set_page_config(page_title="401-OK",page_icon="👌",layout="centered", initial_sidebar_state="collapsed") 

st.write(""" # 401 OK! 👌 """)
if 'config_dict' not in st.session_state:
    st.session_state['config_dict'] = dict()
buttons = st.container()
with buttons:
    c_optimize_btn, c_file_upload_btn = st.columns([1,2])

file_upload_help = """
Please upload a yaml file with the any of the folowing parameters to auto-apply settings. You can copy this and paste it in the file to get a head start.

> ⚠️For now, this only works on the first time you upload a file. This is a known bug. 
```yaml
hsa: 0                          # int annual amount
hsa_match: 0                    # int annual amount
roth_ira: 0                     # int annual amount
trad_401k_rate: 15              # int percent (eg. 15)
roth_401k_rate: 0               # int percent (eg. 10)
salary: 60000                   # int annual amount
min_net_pay: 3500               # int monthly amount
misc_pre_tax_deductions: 1000   # int annual amount
misc_post_tax_deductions: 1000  # int annual amount
brokerage: 0                    # int annual amount
state_local_tax: 5.0            # float percent (eg. 4.5)
```
"""
with c_file_upload_btn:
        config_file = st.file_uploader("Upload Config",type=['yaml','yml'],help=file_upload_help,key='config_file')

if config_file is not None: 
    file_content = config_file.getvalue().decode('utf-8')
    # Load the YAML data
    data = yaml.safe_load(file_content)
    if st.session_state['config_dict'] != data:
        print('setting config again')
        st.session_state.hsa = data.get('hsa',0)
        st.session_state.hsa_match = data.get('hsa_match',0)
        st.session_state.roth_ira = data.get('roth_ira',0)
        st.session_state.trad_401k_rate = data.get('trad_401k_rate',0)
        st.session_state.roth_401k_rate = data.get('roth_401k_rate',0)
        st.session_state.salary = data.get('salary',0)
        st.session_state.min_net_pay = data.get('min_net_pay',0)
        st.session_state.misc_pre_tax_deductions = data.get('misc_pre_tax_deductions',0)
        st.session_state.misc_post_tax_deductions = data.get('misc_post_tax_deductions',0)
        st.session_state.brokerage = data.get('brokerage',0)
        st.session_state.state_local_tax = data.get('state_local_tax',0)
        st.session_state['config_dict'] = data
defaults = [ 
    ('hsa',0),
    ('hsa_match', 0),
    ('roth_ira', 0),
    ('trad_401k_rate', 15),
    ('roth_401k_rate', 0),
    ('salary',60_000),
    ('min_net_pay', 3_500),
    ('misc_pre_tax_deductions',1_000),
    ('misc_post_tax_deductions',1_000),
    ('brokerage',0),
    ('state_local_tax',5.0),
    ('taxable_income',0)
]

for k,v in defaults:
    if k not in st.session_state:
        st.session_state[k] = v

data_points = st.container()
with data_points:
    c_paycheck, c_save_rate, c_save_amt = st.columns(3) 

charts = st.container()
with charts:
    c_buckets, c_limits = st.columns(2)

settings_container = st.container()
with settings_container:
    c_salary, c_pre_tax, c_after_tax, c_misc = st.columns(4)

# debug = st.expander("Debug Info", expanded=False, icon = "🛠️")

with c_salary:
    salary = st.number_input("Annual Salary",step=100, key='salary')
    bonus = st.number_input("Annual Bonus %",0.0,15.0, value=7.5, key='bonus')
    min_net_pay = st.number_input("Minimum Allowed Net Monthly Pay",0, key='min_net_pay')

with c_pre_tax: 
    trad_401k_rate = st.slider("401k Savings Rate", 0, 25,key="trad_401k_rate")
    trad_401k_match_rate = calc_401k_match(st.session_state['trad_401k_rate'],0.5,6)
    st.number_input("401k Match Rate", value=trad_401k_match_rate,disabled=True,key="trad_401k_match_rate")
    hsa = st.number_input("Annual HSA contributions", 0,MAX_HSA,key='hsa')
    hsa_match = st.number_input("Annual HSA employer match", 0,MAX_HSA,value= 1_000,key='hsa_match')
with c_after_tax: 
    roth_401k_rate = st.slider("Roth 401k Savings Rate", 0,25,key='roth_401k_rate')
    roth_ira = st.number_input("Annual Roth IRA Contributions", 0, MAX_ROTH_IRA,key='roth_ira')
    brokerage = st.number_input("After Tax Brokerage Contributions", 0,key='brokerage')
    edu_529 = st.number_input("Annual 529 Savings", 0,value=3_600,key='edu_529')

with c_misc: 
    donations = st.number_input("Annual Charitable Donations", 0, value=1_700,key='donations')

with st.sidebar:
    children = st.number_input("Number of Children",0,10,value=3,key="children")
    pay_periods = st.number_input("Pay Periods Per Year",1,52, value=26,key="pay_periods")
    # annual_spending = st.number_input("Annual Spending Estimate",max_value=salary,value=50_000)
    misc_pre_tax_deductions = st.number_input("Pre Tax Payroll Deductions", 0,key='misc_pre_tax_deductions')
    misc_post_tax_deductions = st.number_input("Post Tax Payroll Deductions", 0,key='misc_post_tax_deductions')
    state_local_income_tax = st.number_input("State and local income tax %",1.,50.0,key='state_local_tax')

salary = st.session_state['salary']
bonus = st.session_state['bonus']/100*salary
st.session_state['bonus_amt'] = st.session_state['bonus']/100*salary
total_salary = salary + st.session_state['bonus_amt']
top_marginal_bracket = min((r for d,r in BRACKETS if d > total_salary), key=lambda x:x)

taxable_income = calculate_taxable_income()
st.session_state['income_tax'] = calculate_tax(taxable_income)-(CHILD_TAX_CREDIT*children)


total_savings_rate = calculate_total_savings_dollars() / total_salary

takehome_paycheck = calculate_total_takehome_paycheck()

money_buckets = {
    "bucket": ["Tax Deferred", "Tax Free", "After Tax"],
    "value": [
        (st.session_state['trad_401k_rate']/100+st.session_state['trad_401k_match_rate']/100)*total_salary,
        (roth_401k_rate/100*total_salary)+roth_ira+hsa+hsa_match+edu_529
        ,brokerage
    ],
    "x": ["","",""],
}

contribution_limits = {
    "fund_name": ["HSA", "HSA", "Roth IRA", "Roth IRA","401k", "401k","Brokerage"],
    "category": ["Contributions","Remaining","Contributions","Remaining","Contributions","Remaining","Contributions"],
    "value": [
        hsa + hsa_match,
        (MAX_HSA - (hsa + hsa_match)) if (MAX_HSA - (hsa + hsa_match)) > 0 else 0,
        roth_ira,
        (MAX_ROTH_IRA - roth_ira) if (MAX_ROTH_IRA - roth_ira) > 0 else 0,
        (st.session_state['trad_401k_rate']/100 + st.session_state['roth_401k_rate']/100 )*total_salary,
        (MAX_401K-((st.session_state['trad_401k_rate']/100+st.session_state['roth_401k_rate']/100)*total_salary)) if (MAX_401K-((st.session_state['trad_401k_rate']/100+st.session_state['roth_401k_rate']/100)*total_salary)) > 0 else 0,
        brokerage],
}


    # final_net = compute_net_monthly()
with c_optimize_btn:
        st.button("Optimize for FOO",key="b_foo_optimize",type="primary",on_click=optimize_for_foo)

with c_paycheck:
    net_monthly_ui = compute_net_monthly()
    st.write("Net Monthly Pay: \n ### ~ $", '{:,.0f}'.format(round(net_monthly_ui)))
with c_save_rate:
    st.write("Total Savings Rate: \n ### ", '{:,.2f}%'.format(total_savings_rate*100))
with c_save_amt:
    st.write("Total Savings Amt: \n ### ~ $", '{:,.0f}'.format(round(total_savings_rate*total_salary)))
    st.write("Monthly: ~ $", '{:,.0f}'.format(round(total_savings_rate*total_salary/12)))


with c_buckets:
    st.bar_chart(money_buckets,x="x", y="value", color="bucket",horizontal=True,stack="normalize",x_label="",y_label="")
with c_limits:
    st.bar_chart(contribution_limits,x="fund_name", y="value", color="category",horizontal=True,stack="normalize",x_label="",y_label="",sort=False)


# with debug: 
    # st.write("Salary: ",total_salary)
    # st.write("Tax: ",st.session_state['income_tax'])
    # st.write("Tax per paycheck: ",st.session_state['income_tax']/pay_periods)
    # st.write("Payckeck: ", takehome_paycheck)
    # st.write("Total Savings : ", total_savings_rate*total_salary)
    # st.write("Total Savings Rate: ", total_savings_rate)
    # st.session_state
