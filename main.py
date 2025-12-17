import streamlit as st
import pandas as pd
import yaml
import time
from datetime import datetime
from src.helper_funcs import calc_401k_match, calculate_tax, calculate_taxable_income,compute_net_monthly, optimize_for_foo,calculate_total_savings_dollars, calculate_total_takehome_paycheck, calculate_investment
from src.globals import MAX_401K,MAX_ROTH_IRA,MAX_HSA,CHILD_TAX_CREDIT,BRACKETS

st.set_page_config(
    page_title="401-OK",
    page_icon="👌",
    layout="centered", 
    initial_sidebar_state="expanded",
    menu_items={
        "Report a bug":"https://github.com/M-Barrows/401-ok/issues",
        "About":"""
            Made with 💛 by [Code and Coffee](https://codecoffee.org). I made this entirely for me. If you find use in it, that's a big win!

            I often found myself drafting up what-if scenarios after catching up with my latest personal finance creators. However, that task involved creating new one-off spreadsheets, tweaking it until the monthly takehome amount was acceptable, generating a monthly savings amount, plugging that into various online calculators, going back to the spreadsheet, etc., etc. It was fun to dream but the workflow was exhausting. 

            That's how 401-ok came to be. I just needed a single place to do all of my experimenting. This tool does NOT rival many of the existing tools out there in terms of number of features. But, what it does do is answer the questions for my specific (very simple) situation and provide instant feedback when changes in allocation are made. I don't plan to make big changes to this tool. But, as I have more questions or what-if scenarios that I can't answer, I will look to expand the tool at that time. 

            If you like my work and want to connect, you can find me here: 

            * [Github](https://github.com/M-Barrows/)
            * [LinkedIn](https://www.linkedin.com/in/michaelabarrows/)
            """
    }) 

c_title, c_optimize_bt = st.columns([2,1],vertical_alignment="bottom")

with c_title:
    st.write(""" # 401 OK! 👌 """)
with c_optimize_bt:
    st.button("Optimize for FOO",key="b_foo_optimize",type="primary",on_click=optimize_for_foo,width="stretch",help="Distribute savings according to [The Money Guy](https://moneyguy.com/guide/foo/)'s Financial Order of Operations")

if 'config_dict' not in st.session_state:
    st.session_state['config_dict'] = dict()
sidebar = st.sidebar

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
children: 1                     # int
pay_periods: 26                 # int
years_to_retirement: 25         # int
initial_retirement_balance: 500 # int
expected_investment_return: 8   # int percent (eg. 8)
```
"""

data_points = st.container(horizontal_alignment="center",gap=None)
with data_points:
    c_paycheck, c_save_rate, c_save_amt = st.columns(3) 


charts = st.container()
with charts:
    c_buckets, c_limits = st.columns(2)

retirement_outlook = st.expander("📈 Forecast View")
with retirement_outlook:
    c_retirement_journey_chart, c_retirement_journey_commentary = st.columns([2,1])

errors = st.container()

settings_container = st.expander("🔧 Settings",expanded=True)
with settings_container:
    c_salary, c_pre_tax, c_after_tax, c_misc, c_config = st.tabs(["Salary","Pre-Tax","After Tax","Misc","Config"])

with c_config:
    c_up_config, c_down_config = st.columns([2,1])

with c_up_config:
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
        st.session_state.salary = data.get('salary',100)
        st.session_state.min_net_pay = data.get('min_net_pay',0)
        st.session_state.misc_pre_tax_deductions = data.get('misc_pre_tax_deductions',0)
        st.session_state.misc_post_tax_deductions = data.get('misc_post_tax_deductions',0)
        st.session_state.brokerage = data.get('brokerage',0)
        st.session_state.state_local_tax = data.get('state_local_tax',0)
        st.session_state.children = data.get('children',0)
        st.session_state.pay_periods = data.get('pay_periods',0)
        st.session_state.years_to_retirement = data.get('years_to_retirement',25)
        st.session_state.initial_retirement_balance = data.get('initial_retirement_balance',500)
        st.session_state.expected_investment_return = data.get('expected_investment_return',8)
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

# debug = st.expander("Debug Info", expanded=False, icon = "🛠️")

with c_salary:
    salary = st.number_input("Annual Salary",min_value=100,step=100, key='salary')
    pay_periods = st.number_input("Pay Periods Per Year",1,52, value=26,key="pay_periods")
    bonus = st.number_input("Annual Bonus %",0.0,15.0, value=7.5, key='bonus')
    min_net_pay = st.number_input("Minimum Allowed Net Monthly Pay",0, key='min_net_pay')

max401k_perc = int((MAX_401K*100)/(salary*100)*100)
with c_pre_tax: 
    trad_401k_rate = st.slider("401k Savings Rate", 0, max401k_perc ,key="trad_401k_rate")
    trad_401k_match_rate = calc_401k_match(st.session_state['trad_401k_rate'],0.5,6)
    st.number_input("401k Match Rate", value=trad_401k_match_rate,key="trad_401k_match_rate")
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

with c_paycheck:
    net_monthly_ui = compute_net_monthly()
    st.metric("💸 Your Paycheck", 
              "~ $"+'{:,.0f}'.format(round(net_monthly_ui)),
              "~ $"+'{:,.0f}'.format(round(net_monthly_ui*12))+' Yearly',
              border=True,
              height="stretch",
              delta_color="off",
              delta_arrow="off")
with c_save_rate:
    st.metric("📈 Savings Rate",
              '{:,.2f}%'.format(total_savings_rate*100),
              border=True,
              height="stretch")
with c_save_amt:
    st.metric(
          "🏦 Total Savings",
          "~ $"+'{:,.0f}'.format(round(total_savings_rate*total_salary)),
          "$"+'{:,.0f}'.format(round(total_savings_rate*total_salary/12))+" Monthly",
          border=True,
          delta_arrow="off",
          delta_color="off"
    )


with c_buckets:
    st.bar_chart(money_buckets,x="x", y="value", color="bucket",horizontal=True,stack="normalize",x_label="",y_label="")
with c_limits:
    st.bar_chart(contribution_limits,x="fund_name", y="value", color="category",horizontal=True,stack="normalize",x_label="",y_label="",sort=False)

config_obj = {
    "hsa": st.session_state.get('hsa',0),
    "hsa_match": st.session_state.get('hsa_match',0),
    "roth_ira": st.session_state.get('roth_ira',0),
    "trad_401k_rate": st.session_state.get('trad_401k_rate',0),
    "roth_401k_rate": st.session_state.get('roth_401k_rate',0),
    "salary": st.session_state.get('salary',100),
    "min_net_pay": st.session_state.get('min_net_pay',st.session_state.get('salary')),
    "misc_pre_tax_deductions": st.session_state.get('misc_pre_tax_deductions',0), 
    "misc_post_tax_deductions": st.session_state.get('misc_post_tax_deductions',0),
    "brokerage": st.session_state.get('brokerage',0), 
    "state_local_tax": st.session_state.get('state_local_tax',0),
    "children": st.session_state.get('children',0),
    "pay_periods": st.session_state.get('pay_periods',0),
    "years_to_retirement": st.session_state.get('years_to_retirement',25),
    "initial_retirement_balance": st.session_state.get('initial_retirement_balance',0),
    "expected_investment_return": st.session_state.get('expected_investment_return',8),
}
with c_down_config:
    try:
        config_file = st.download_button("Download Config",icon="💾", data=yaml.dump(config_obj), file_name="401-ok-config.yaml",mime="text/plain",key='config_obj')
    except: 
        st.exception("Config could not be downloaded")
    finally:
        if config_file:
            time.sleep(5)
            st.toast("Your config has been saved",icon="💾",duration=10)

growth_df = calculate_investment(
    st.session_state.get('initial_retirement_balance',500),
    total_salary*total_savings_rate,
    st.session_state.get('years_to_retirement',25),
    st.session_state.get('expected_investment_return',8)
)

with c_retirement_journey_commentary:
    st.write(f"**Ending Balance: ${'{:,.0f}'.format(growth_df.iloc[-1]['Total'])}**")
    st.number_input("Years Until Retirement",min_value=1,max_value=50,value=25,key="years_to_retirement")
    st.number_input("Initial Retirement Balance",min_value=0,value=50_000,key="initial_retirement_balance")
    st.number_input("Expected Return %",min_value=1.0,max_value=50.0,value=8.0,key="expected_investment_return",format="%0.1f")


with c_retirement_journey_chart:
    # st.dataframe(growth_df)
    st.bar_chart(data = growth_df, x='Year',y=['Starting Balance','Contributions','Growth'],sort=False)

# with debug: 
#     st.write("Salary: ",total_salary)
#     st.write("Tax: ",st.session_state['income_tax'])
#     st.write("Tax per paycheck: ",st.session_state['income_tax']/pay_periods)
#     st.write("Payckeck: ", takehome_paycheck)
#     st.write("Total Savings : ", total_savings_rate*total_salary)
#     st.write("Total Savings Rate: ", total_savings_rate)
#     st.session_state
