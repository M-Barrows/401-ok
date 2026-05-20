import streamlit as st
from tools.globals import ACCOUNT_KEYS
from tools.helper_funcs import calculate_annual_contributions_by_account, calculate_bonus_takehome, calculate_investment, calculate_total_savings_dollars, calculate_total_starting_balance, compute_net_monthly, get_current_balance_by_account, get_expected_returns_by_account, nest_egg_forecast_by_account_df


def paycheck_metric():
    monthly_paycheck = compute_net_monthly()
    bonus_takehome = calculate_bonus_takehome()
    annual_total = (monthly_paycheck * 12) + bonus_takehome
    return st.metric("💸 Your Paycheck",
      "~ $"+'{:,.0f}'.format(monthly_paycheck),
      "~ $"+'{:,.0f}'.format(annual_total)+' Yearly',
      border=True,
      height="stretch",
      delta_color="off",
      delta_arrow="off")

def savings_rate_metric():
    savings_for_rate, _ = calculate_total_savings_dollars()
    return st.metric("📈 Savings Rate",
              '{:,.2f}%'.format(savings_for_rate/st.session_state['total_salary']*100),
              border=True,
              height="stretch")
def savings_amt_metric():
    _, total_savings = calculate_total_savings_dollars()
    return st.metric(
          "🏦 Total Savings",
          "~ $"+'{:,.0f}'.format(round(total_savings)),
          "$"+'{:,.0f}'.format(round(total_savings/12))+" Monthly",
          border=True,
          delta_arrow="off",
          delta_color="off"
    )
def nest_egg_metric():
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
    final_portfolio_value = chart_df.groupby(['Year']).sum().reset_index()['Total'].iloc[-1]
    return st.metric(
          "📈 Projected Nest Egg",
          "~ $"+'{:,.0f}'.format(round(final_portfolio_value)),
          "~ $"+'{:,.0f}'.format(round(final_portfolio_value*0.047)) + " Yearly",
          border=True,
          delta_arrow="off",
          delta_color="off",
          height = "stretch"
    )
__all__ = ['paycheck_metric','savings_rate_metric','savings_amt_metric','nest_egg_metric']
