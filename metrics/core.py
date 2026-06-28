import streamlit as st
from tools.globals import ACCOUNT_KEYS
from tools.helper_funcs import calculate_annual_contributions_by_account, calculate_bonus_takehome, calculate_investment, calculate_total_savings_dollars, calculate_total_starting_balance, compute_net_monthly, get_current_balance_by_account, get_expected_returns_by_account, nest_egg_forecast_by_account_df


def paycheck_metric():
    monthly_paycheck = compute_net_monthly()
    bonus_takehome = calculate_bonus_takehome()
    annual_total = (monthly_paycheck * 12) + bonus_takehome
    return st.metric("💸 Your Paycheck",
                     f"~ ${monthly_paycheck:,.0f}",
                     f"~ ${annual_total:,.0f} / yr",
                     help=f"Yearly total includes \\${bonus_takehome:,.0f} bonus takehome payment(s)",
                     border=True,
                     height="stretch",
                     delta_color="off",
                     delta_arrow="off")


def savings_rate_metric():
    savings_for_rate, total_savings, savings_529 = calculate_total_savings_dollars()
    total_salary = st.session_state.get('total_salary', 60000)
    savings_rate = (savings_for_rate / total_salary * 100) if total_salary > 0 else 0
    return st.metric("📈 Savings Rate",
                     f"{savings_rate:.2f}%",
                     help=f"Saving \\${savings_for_rate:,.0f} of \\${total_salary:,.0f} total compensation including bonuses (+ employer match)",
                     border=True,
                     height="stretch")


def savings_amt_metric():
    savings_for_rate, total_savings, savings_529 = calculate_total_savings_dollars()
    monthly = total_savings / 12
    tooltip = f"\\$ {savings_for_rate:,.0f} invested"
    if savings_529 > 0:
        tooltip += f" + \\${savings_529:,.0f} in a 529"
    return st.metric("🏦 Total Savings",
                     f"~ ${monthly:,.0f}",
                     f"~ ${total_savings:,.0f} / yr",
                     help=tooltip,
                     border=True,
                     delta_arrow="off",
                     delta_color="off")


def nest_egg_metric():
    contributions = calculate_annual_contributions_by_account()
    df = nest_egg_forecast_by_account_df({
        account: {
            'start_balance': get_current_balance_by_account()[account],
            'contributions': contributions.get(account, 0),
            'expected_return': get_expected_returns_by_account()[account],
        }
        for account in ACCOUNT_KEYS
    })

    if st.session_state.get('spousal_enabled', False):
        primary_years = st.session_state.get('years_to_retirement', 25)
        spouse_years = st.session_state.get('spouse_years_to_retirement', 25)
        max_years = max(primary_years, spouse_years)

        spouse_contributions = calculate_annual_contributions_by_account(spouse=True)
        spouse_df = nest_egg_forecast_by_account_df({
            account: {
                'start_balance': get_current_balance_by_account(spouse=True)[account],
                'contributions': spouse_contributions.get(account, 0),
                'expected_return': get_expected_returns_by_account(spouse=True)[account],
            }
            for account in ['roth_ira', 'hsa', 'roth_401k', 'trad_401k', 'brokerage']
        }, years_to_retirement=max_years)

        if not df.empty and not spouse_df.empty:
            df = nest_egg_forecast_by_account_df({
                account: {
                    'start_balance': get_current_balance_by_account()[account],
                    'contributions': contributions.get(account, 0),
                    'expected_return': get_expected_returns_by_account()[account],
                }
                for account in ACCOUNT_KEYS
            }, years_to_retirement=max_years)
            df = df._append(spouse_df, ignore_index=True)
        elif not spouse_df.empty:
            df = spouse_df

    if df.empty:
        st.metric("📈 Projected Nest Egg", "$0",
                  help="Add account starting balances and contributions to see your forecast")
        return

    latest = df[df['Year'] == df['Year'].max()]
    if latest.empty:
        st.metric("📈 Projected Nest Egg", "$0")
        return

    total = latest['Total'].sum()
    contribs = latest['Contributions'].sum()
    growth = latest['Growth'].sum()
    return st.metric("📈 Projected Nest Egg",
                     f"~ ${total:,.0f}",
                     f"~ ${total*0.047:,.0f} / yr",
                     help=f"\\${contribs:,.0f} in contributions + \\${growth:,.0f} in growth",
                     border=True,
                     delta_arrow="off",
                     delta_color="off",
                     height="stretch")
