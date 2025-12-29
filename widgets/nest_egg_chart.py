from tools.helper_funcs import calculate_total_savings_dollars,calculate_investment
import streamlit as st
import pandas as pd

def calculate_annual_contributions_by_account():
    annual_contributions = dict()
    annual_contributions['roth_401k'] = st.session_state.get('roth_401k_rate') * st.session_state.get('salary')
    annual_contributions['trad_401k'] = (st.session_state.get('trad_401k_rate') + st.session_state.get('trad_401k_match_rate'))/100 * st.session_state.get('salary')
    annual_contributions['hsa'] = st.session_state.get('hsa') + st.session_state.get('hsa_match')
    annual_contributions['roth_ira'] = st.session_state.get('roth_ira')
    annual_contributions['brokerage'] = st.session_state.get('brokerage')
    annual_contributions['edu_529'] = st.session_state.get('edu_529')
    return annual_contributions

def nest_egg_forecast_contrib_v_growth_df():
    total_savings_rate = calculate_total_savings_dollars() / st.session_state.get('total_salary',60_000)
    growth_df = calculate_investment(
        st.session_state.get('initial_retirement_balance',500),
        st.session_state.get('total_salary',60_000)*total_savings_rate,
        st.session_state.get('years_to_retirement',25),
        st.session_state.get('expected_investment_return',8)
    )
    return growth_df

def nest_egg_forecast_by_account_df(contribution_dict:dict):
    full_df = pd.DataFrame()
    for account,contribution in contribution_dict.items():
        df = calculate_investment(
            0,
            contribution,
            st.session_state.get('years_to_retirement',25),
            st.session_state.get('expected_investment_return',8)
        )
        df['Account'] = account
        df['Total'] = df['Total'].round(2)
        if df['Total'].max() > 0:
            full_df = pd.concat([full_df,df[['Year','Account','Total']]])
    return full_df

def nest_egg_forecast_chart(): 
    retirement_outlook = st.expander("📈 Forecast View",expanded=True)

    with retirement_outlook:
        c_retirement_journey_chart, c_retirement_journey_commentary = st.columns([2,1])
        
        with c_retirement_journey_chart:
            t_contributions, t_account = st.tabs(['Contributions','Account'])
        
        with t_contributions:
            chart_df = nest_egg_forecast_contrib_v_growth_df()
            st.bar_chart(data = chart_df, x='Year',y=['Starting Balance','Contributions','Growth'],sort=False)
        
        with t_account:
            chart_df = nest_egg_forecast_by_account_df(calculate_annual_contributions_by_account())
            chart_df['Account'] = chart_df.apply(lambda X: X.Account.replace('_',' ').title(), axis = 1)
            st.bar_chart(data = chart_df, x='Year',y='Total',color='Account',sort='Total')
       
        with c_retirement_journey_commentary:
            st.write(f"**Ending Balance: ${'{:,.0f}'.format(chart_df.groupby('Year').sum().iloc[-1]['Total'])}**")
            st.number_input("Years Until Retirement",min_value=1,max_value=50,key="years_to_retirement")
            # st.number_input("Initial Retirement Balance",min_value=0,key="initial_retirement_balance")
            st.number_input("Expected Return %",min_value=1.0,max_value=50.0,key="expected_investment_return",format="%0.1f")

