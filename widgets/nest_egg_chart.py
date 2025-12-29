from tools.globals import ACCOUNT_KEYS
from tools.helper_funcs import calculate_annual_contributions_by_account, calculate_total_savings_dollars,calculate_investment, calculate_total_starting_balance, get_current_balance_by_account, get_expected_returns_by_account, nest_egg_forecast_by_account_df
import streamlit as st
import pandas as pd



# def nest_egg_forecast_contrib_v_growth_df():
#     total_savings_rate = calculate_total_savings_dollars() / st.session_state.get('total_salary',60_000)
#     growth_df = calculate_investment(
#         calculate_total_starting_balance(),
#         st.session_state.get('total_salary',60_000)*total_savings_rate,
#         st.session_state.get('years_to_retirement',25),
#         st.session_state.get('expected_investment_return',8)
#     )
#     return growth_df


def nest_egg_forecast_chart(): 
    retirement_outlook = st.expander("📈 Forecast View",expanded=True)

    with retirement_outlook:
        c_retirement_journey_chart, c_retirement_journey_commentary = st.columns([2,1])
        
        with c_retirement_journey_chart:
            t_contributions, t_account = st.tabs(['Contributions','Account'])
            contributions = calculate_annual_contributions_by_account()
            expected_returns = get_expected_returns_by_account()
            starting_balance = get_current_balance_by_account()
            config_dict = dict()
            for account in ACCOUNT_KEYS:
                config_dict.update( 
                    {
                        account: {
                            'expected_return': expected_returns[account],
                            'start_balance': starting_balance[account],
                            'contributions': contributions[account]
                        }
                    }
                )

            chart_df = nest_egg_forecast_by_account_df(config_dict)
            chart_df['Account'] = chart_df.apply(lambda X: X.Account.replace('_',' ').title(), axis = 1)
        
        with t_contributions:
            chart_df_grouped = chart_df.groupby(['Year']).sum().reset_index()
            st.bar_chart(data = chart_df_grouped, x='Year',y=['Starting Balance','Contributions','Growth'],sort=False)
        
        with t_account:
            st.bar_chart(data = chart_df, x='Year',y='Total',color='Account',sort='Total')
       
        with c_retirement_journey_commentary:
            st.write(f"**Ending Balance: ${'{:,.0f}'.format(chart_df.groupby('Year').sum().iloc[-1]['Total'])}**")
            st.number_input("Years Until Retirement",min_value=1,max_value=50,key="years_to_retirement")
            # st.number_input("Initial Retirement Balance",min_value=0,key="initial_retirement_balance")
            # st.number_input("Expected Return %",min_value=1.0,max_value=50.0,key="expected_investment_return",format="%0.1f")
