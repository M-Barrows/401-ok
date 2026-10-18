import streamlit as st
from tools.globals import ACCOUNT_KEYS, BRACKETS_JOINT, BRACKETS_SINGLE, CHILD_TAX_CREDIT, STANDARD_DEDUCTION, STANDARD_DEDUCTION_SINGLE
from tools.helper_funcs import calculate_annual_contributions_by_account, calculate_bonus_takehome, calculate_investment, calculate_tax, calculate_total_savings_dollars, calculate_total_starting_balance, compute_net_monthly, get_bonus_amount, get_current_balance_by_account, get_expected_returns_by_account, get_spouse_bonus_amount, nest_egg_forecast_by_account_df


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


def effective_tax_bracket_metric():
    spousal = st.session_state.get('spousal_enabled', False)
    filing_jointly = st.session_state.get('filing_jointly', True) if spousal else True
    brackets = BRACKETS_JOINT if filing_jointly else BRACKETS_SINGLE
    std_ded = STANDARD_DEDUCTION if filing_jointly else STANDARD_DEDUCTION_SINGLE

    primary_salary = st.session_state.get('salary', 60000)
    primary_bonus = get_bonus_amount()
    spouse_salary = st.session_state.get('spouse_salary', 0) if spousal else 0
    spouse_bonus = get_spouse_bonus_amount() if spousal else 0

    total_income = primary_salary + primary_bonus + spouse_salary + spouse_bonus

    trad_401k_dollars = (st.session_state.get('trad_401k_rate', 0) / 100) * primary_salary
    hsa_total = st.session_state.get('hsa', 0)
    misc_pre = st.session_state.get('misc_pre_tax_deductions', 0)
    donations = st.session_state.get('donations', 0)

    spouse_trad = 0
    spouse_hsa = 0
    spouse_misc_pre = 0
    spouse_donations = 0
    if spousal:
        spouse_trad = (st.session_state.get('spouse_trad_401k_rate', 0) / 100) * spouse_salary
        spouse_hsa = st.session_state.get('spouse_hsa', 0)
        spouse_misc_pre = st.session_state.get('spouse_misc_pre_tax_deductions', 0)
        spouse_donations = st.session_state.get('spouse_donations', 0)

    total_pre_tax = trad_401k_dollars + hsa_total + misc_pre + donations \
                    + spouse_trad + spouse_hsa + spouse_misc_pre + spouse_donations

    ti = total_income - std_ded - total_pre_tax
    income_tax = calculate_tax(ti, brackets) - (
        CHILD_TAX_CREDIT * st.session_state.get('children', 0)
    )

    effective_rate = (income_tax / total_income * 100) if total_income > 0 else 0

    highest_rate = brackets[-1][1]
    for limit, rate in brackets:
        if ti <= limit:
            highest_rate = rate
            break

    return st.metric("💰 Current Effective Tax Bracket",
                     f"{effective_rate:.1f}%",
                     f"~ ${income_tax:,.0f} / yr",
                     help=f"Highest Tax Bracket: {highest_rate*100:.0f}%",
                     border=True,
                     height="stretch",
                     delta_color="off",
                     delta_arrow="off")


def contribution_room_metric():
    spousal = st.session_state.get('spousal_enabled', False)

    primary_salary = st.session_state.get('salary', 60000)
    bonus_amt = get_bonus_amount()
    total_salary = st.session_state.get('total_salary', primary_salary + bonus_amt)

    trad_401k_dollars = (st.session_state.get('trad_401k_rate', 0) / 100) * primary_salary
    trad_401k_from_bonus = (st.session_state.get('trad_401k_rate', 0) / 100) * bonus_amt
    hsa_dollars = st.session_state.get('hsa', 0)

    spouse_salary = st.session_state.get('spouse_salary', 0) if spousal else 0
    spouse_bonus_amt = get_spouse_bonus_amount() if spousal else 0
    spouse_trad_401k = (st.session_state.get('spouse_trad_401k_rate', 0) / 100) * spouse_salary if spousal else 0
    spouse_trad_from_bonus = (st.session_state.get('spouse_trad_401k_rate', 0) / 100) * spouse_bonus_amt if spousal else 0
    spouse_hsa = st.session_state.get('spouse_hsa', 0) if spousal else 0

    filing_jointly = st.session_state.get('filing_jointly', True) if spousal else True
    brackets = BRACKETS_JOINT if filing_jointly else BRACKETS_SINGLE

    marginal_rate = brackets[-1][1]
    for limit, rate in brackets:
        if total_salary <= limit:
            marginal_rate = rate
            break

    pre_tax_contributions = trad_401k_dollars + trad_401k_from_bonus + hsa_dollars \
                           + spouse_trad_401k + spouse_trad_from_bonus + spouse_hsa
    tax_savings = pre_tax_contributions * marginal_rate

    return st.metric("💰 Tax Savings from Retirement Accounts",
                     f"${tax_savings:,.0f}",
                     border=True,
                     height="stretch",
                     delta_color="off",
                     delta_arrow="off")
