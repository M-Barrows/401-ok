from .globals import ACCOUNT_KEYS, SPOUSE_ACCOUNT_KEYS, STANDARD_DEDUCTION, STANDARD_DEDUCTION_SINGLE, BRACKETS_JOINT, BRACKETS_SINGLE, CHILD_TAX_CREDIT, MAX_HSA, MAX_ROTH_IRA, MAX_401K, ROTH_IRA_PHASE_OUT_SINGLE, ROTH_IRA_PHASE_OUT_JOINT, ROTH_IRA_CATCHUP
import streamlit as st
import pandas as pd
from datetime import datetime


def get_bonus_amount():
    return st.session_state.get('bonus', 7.5) / 100 * st.session_state.get('salary', 60000)


def get_spouse_bonus_amount():
    return st.session_state.get('spouse_bonus', 7.5) / 100 * st.session_state.get('spouse_salary', 60000)


def get_effective_magi(spouse=False):
    primary_magi = (
        st.session_state['salary']
        + get_bonus_amount()
        - (st.session_state.get('trad_401k_rate', 0) / 100 * st.session_state['salary'])
        - st.session_state.get('hsa', 0)
        - st.session_state.get('misc_pre_tax_deductions', 0)
        - st.session_state.get('donations', 0)
    )
    if not st.session_state.get('spousal_enabled', False):
        return max(0, primary_magi)

    spouse_magi = (
        st.session_state.get('spouse_salary', 0)
        + get_spouse_bonus_amount()
        - (st.session_state.get('spouse_trad_401k_rate', 0) / 100 * st.session_state.get('spouse_salary', 0))
        - st.session_state.get('spouse_hsa', 0)
        - st.session_state.get('spouse_misc_pre_tax_deductions', 0)
        - st.session_state.get('spouse_donations', 0)
    )

    if spouse and st.session_state.get('filing_jointly', True):
        return max(0, primary_magi + spouse_magi)
    elif spouse:
        return max(0, spouse_magi)
    else:
        return max(0, primary_magi)


def calculate_roth_ira_max(magi, age, filing_jointly):
    per_person_base = MAX_ROTH_IRA + (ROTH_IRA_CATCHUP if age >= 50 else 0)

    phase_out_start, phase_out_end = (
        ROTH_IRA_PHASE_OUT_JOINT if filing_jointly else ROTH_IRA_PHASE_OUT_SINGLE
    )

    if magi < phase_out_start:
        return per_person_base
    elif magi >= phase_out_end:
        return 0
    else:
        reduction_ratio = (magi - phase_out_start) / (phase_out_end - phase_out_start)
        reduced = per_person_base * (1 - reduction_ratio)
        return max(0, int(reduced))


def calculate_bonus_takehome():
    bonus_amt = get_bonus_amount()
    bonus_401k = (st.session_state.get('trad_401k_rate', 0) / 100) * bonus_amt
    bonus_roth = (st.session_state.get('roth_401k_rate', 0) / 100) * bonus_amt
    bonus_tax = bonus_amt * 0.22
    return bonus_amt - bonus_tax - bonus_401k - bonus_roth


def calculate_taxable_income_salary_only(**kwargs):
    salary = kwargs.get('salary', st.session_state['salary'])
    hsa = kwargs.get('hsa', st.session_state['hsa'])
    donations = kwargs.get('donations', st.session_state['donations'])
    misc_pre_tax_deductions = kwargs.get('misc_pre_tax_deductions', st.session_state['misc_pre_tax_deductions'])
    trad_401k_rate = kwargs.get('trad_401k_rate', st.session_state.get('trad_401k_rate', 0)) / 100
    std_ded = kwargs.get('std_deduction', STANDARD_DEDUCTION)

    st.session_state['taxable_income_salary_only'] = (
        salary
        - std_ded
        - (trad_401k_rate * salary)
        - hsa
        - misc_pre_tax_deductions
        - donations
    )
    return st.session_state['taxable_income_salary_only']


def calc_401k_match(savings_rate: float, match: float, limit: float):
    if savings_rate == 0: 
        return 0
    if savings_rate < limit: 
        return savings_rate * match
    else:
        return match * limit


def calculate_taxable_income(**kwargs):
    salary = kwargs.get('salary', st.session_state['salary'])
    bonus = kwargs.get('bonus', st.session_state['bonus'])
    hsa = kwargs.get('hsa', st.session_state['hsa'])
    donations = kwargs.get('donations', st.session_state['donations'])
    misc_pre_tax_deductions = kwargs.get('misc_pre_tax_deductions', st.session_state['misc_pre_tax_deductions'])
    trad_401k_rate = kwargs.get('trad_401k_rate', st.session_state.get('trad_401k_rate', 0)) / 100
    std_ded = kwargs.get('std_deduction', STANDARD_DEDUCTION)
    bonus_amount = bonus / 100 * salary if bonus else 0
    taxable = (
        (salary + bonus_amount)
        - std_ded
        - (trad_401k_rate * (salary + bonus_amount))
        - hsa
        - misc_pre_tax_deductions
        - donations
    )
    st.session_state['taxable_income'] = taxable
    return taxable


def calculate_tax(taxable_income, brackets=BRACKETS_JOINT):
    tax = 0.0
    previous_limit = 0.0
    for limit, rate in brackets:
        if limit is None or taxable_income <= limit:
            tax += (taxable_income - previous_limit) * rate
            break
        else:
            tax += (limit - previous_limit) * rate
            previous_limit = limit

    for i in [0.062, 0.0145, st.session_state['state_local_tax'] / 100]:
        tax += taxable_income * i
    return tax


def compute_net_monthly():
    spousal = st.session_state.get('spousal_enabled', False)
    filing_jointly = st.session_state.get('filing_jointly', True) if spousal else True
    brackets = BRACKETS_JOINT if filing_jointly else BRACKETS_SINGLE
    std_ded = STANDARD_DEDUCTION if filing_jointly else STANDARD_DEDUCTION_SINGLE
    pay_periods = st.session_state.get('pay_periods', 26)

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
    st.session_state['income_tax'] = income_tax

    if spousal:
        st.session_state['spouse_income_tax'] = income_tax

    roth_ira_pp = st.session_state['roth_ira'] / pay_periods
    brokerage_pp = st.session_state['brokerage'] / pay_periods
    hsa_pp = st.session_state['hsa'] / pay_periods
    misc_post_pp = st.session_state['misc_post_tax_deductions'] / pay_periods
    misc_pre_pp = st.session_state['misc_pre_tax_deductions'] / pay_periods
    donations_pp = st.session_state.get('donations', 0) / pay_periods
    edu_529_pp = st.session_state['edu_529'] / pay_periods
    trad_pp = (st.session_state['trad_401k_rate'] / 100) * st.session_state['salary'] / pay_periods
    roth_pp = (st.session_state['roth_401k_rate'] / 100) * st.session_state['salary'] / pay_periods

    spouse_roth_ira_pp = 0
    spouse_brokerage_pp = 0
    spouse_hsa_pp = 0
    spouse_misc_post_pp = 0
    spouse_misc_pre_pp = 0
    spouse_donations_pp = 0
    spouse_trad_pp = 0
    spouse_roth_pp = 0
    spouse_salary_pp = 0
    if spousal:
        spouse_roth_ira_pp = st.session_state.get('spouse_roth_ira', 0) / pay_periods
        spouse_brokerage_pp = st.session_state.get('spouse_brokerage', 0) / pay_periods
        spouse_hsa_pp = st.session_state.get('spouse_hsa', 0) / pay_periods
        spouse_misc_post_pp = st.session_state.get('spouse_misc_post_tax_deductions', 0) / pay_periods
        spouse_misc_pre_pp = st.session_state.get('spouse_misc_pre_tax_deductions', 0) / pay_periods
        spouse_donations_pp = st.session_state.get('spouse_donations', 0) / pay_periods
        spouse_trad_pp = (st.session_state.get('spouse_trad_401k_rate', 0) / 100) * spouse_salary / pay_periods
        spouse_roth_pp = (st.session_state.get('spouse_roth_401k_rate', 0) / 100) * spouse_salary / pay_periods
        spouse_salary_pp = spouse_salary / pay_periods

    tax_pp = income_tax / pay_periods

    primary_takehome_pp = (
        primary_salary / pay_periods
        - trad_pp - roth_pp
        - roth_ira_pp - brokerage_pp - hsa_pp
        - tax_pp
        - misc_post_pp - misc_pre_pp
        - donations_pp - edu_529_pp
    )

    spouse_takehome_pp = 0
    if spousal and filing_jointly:
        spouse_takehome_pp = (
            spouse_salary_pp
            - spouse_trad_pp - spouse_roth_pp
            - spouse_roth_ira_pp - spouse_brokerage_pp - spouse_hsa_pp
            - spouse_misc_post_pp - spouse_misc_pre_pp
            - spouse_donations_pp
        )
    elif spousal and not filing_jointly:
        spouse_ti = spouse_salary + spouse_bonus - std_ded - (
            spouse_trad + spouse_hsa + spouse_misc_pre + spouse_donations
        )
        spouse_tax = calculate_tax(spouse_ti, brackets)
        spouse_tax_pp = spouse_tax / pay_periods
        spouse_takehome_pp = (
            spouse_salary_pp
            - spouse_trad_pp - spouse_roth_pp
            - spouse_roth_ira_pp - spouse_brokerage_pp - spouse_hsa_pp
            - spouse_tax_pp
            - spouse_misc_post_pp - spouse_misc_pre_pp
            - spouse_donations_pp
        )

    return (primary_takehome_pp + spouse_takehome_pp) * 2


def calculate_total_savings_dollars():
    bonus_amt = get_bonus_amount()

    trad_401k_dollars = (st.session_state.get('trad_401k_rate', 0) / 100) * st.session_state['salary']
    trad_401k_from_bonus = (st.session_state.get('trad_401k_rate', 0) / 100) * bonus_amt
    trad_match_dollars = (st.session_state.get('trad_401k_match_rate', 0)) / 100 * st.session_state['salary']
    roth_401k_dollars = (st.session_state['roth_401k_rate'] / 100) * st.session_state['salary']
    roth_401k_from_bonus = (st.session_state['roth_401k_rate'] / 100) * bonus_amt
    roth_ira_dollars = st.session_state['roth_ira']
    hsa_dollars = st.session_state['hsa']
    hsa_match_dollars = st.session_state.get('hsa_match', 0)
    brokerage_dollars = st.session_state['brokerage']
    edu_529_dollars = st.session_state.get('edu_529', 0)

    primary_savings = (
        trad_401k_dollars + trad_401k_from_bonus + trad_match_dollars
        + roth_401k_dollars + roth_401k_from_bonus
        + roth_ira_dollars + hsa_dollars + hsa_match_dollars + brokerage_dollars
    )

    spouse_savings = 0
    if st.session_state.get('spousal_enabled', False):
        spouse_bonus_amt = get_spouse_bonus_amount()
        s_salary = st.session_state.get('spouse_salary', 0)
        s_trad = (st.session_state.get('spouse_trad_401k_rate', 0) / 100) * s_salary
        s_trad_bonus = (st.session_state.get('spouse_trad_401k_rate', 0) / 100) * spouse_bonus_amt
        s_match = (st.session_state.get('spouse_trad_401k_match_rate', 0) / 100) * s_salary
        s_roth = (st.session_state.get('spouse_roth_401k_rate', 0) / 100) * s_salary
        s_roth_bonus = (st.session_state.get('spouse_roth_401k_rate', 0) / 100) * spouse_bonus_amt
        s_roth_ira = st.session_state.get('spouse_roth_ira', 0)
        s_hsa = st.session_state.get('spouse_hsa', 0)
        s_hsa_match = st.session_state.get('spouse_hsa_match', 0)
        s_brokerage = st.session_state.get('spouse_brokerage', 0)
        spouse_savings = (
            s_trad + s_trad_bonus + s_match
            + s_roth + s_roth_bonus
            + s_roth_ira + s_hsa + s_hsa_match + s_brokerage
        )

    savings_for_rate = primary_savings + spouse_savings
    include_529 = st.session_state.get('include_529_in_nest_egg', True)
    total_savings_dollars = savings_for_rate + (edu_529_dollars if include_529 else 0)
    savings_529 = edu_529_dollars if include_529 else 0

    return savings_for_rate, total_savings_dollars, savings_529


def calculate_total_takehome_paycheck():
    primary = (
        st.session_state['salary']
        - (st.session_state['trad_401k_rate'] / 100 * st.session_state['salary'])
        - (st.session_state['roth_401k_rate'] / 100 * st.session_state['salary'])
        - st.session_state['roth_ira']
        - st.session_state['brokerage']
        - st.session_state['hsa']
        - st.session_state['income_tax']
        - st.session_state['misc_post_tax_deductions']
        - st.session_state['misc_pre_tax_deductions']
        - st.session_state['donations']
    ) / st.session_state['pay_periods']

    if not st.session_state.get('spousal_enabled', False):
        return primary

    spouse = (
        st.session_state.get('spouse_salary', 0)
        - (st.session_state.get('spouse_trad_401k_rate', 0) / 100 * st.session_state.get('spouse_salary', 0))
        - (st.session_state.get('spouse_roth_401k_rate', 0) / 100 * st.session_state.get('spouse_salary', 0))
        - st.session_state.get('spouse_roth_ira', 0)
        - st.session_state.get('spouse_brokerage', 0)
        - st.session_state.get('spouse_hsa', 0)
        - st.session_state.get('spouse_income_tax', 0)
        - st.session_state.get('spouse_misc_post_tax_deductions', 0)
        - st.session_state.get('spouse_misc_pre_tax_deductions', 0)
        - st.session_state.get('spouse_donations', 0)
    ) / st.session_state['pay_periods']

    return primary + spouse


def optimize_for_foo():
    pass


def calculate_investment(starting_balance: int, annual_contribution, years_to_retirement: 
int = 25, growth_rate: int = 8):

    this_year = datetime.now().year
    years = range(this_year, this_year + years_to_retirement)

    start_balance = [starting_balance] * len(years)
    contributions = [0] * len(years)
    growth = [0.0] * len(years)
    total = [0.0] * len(years)
    total[0] = starting_balance
    for i in range(1, len(years)):
        contributions[i] = contributions[i-1] + annual_contribution
        growth[i] = growth[i - 1] + (total[i - 1] * growth_rate / 100)
        total[i] = start_balance[i] + contributions[i] + growth[i]

    df = pd.DataFrame({
        'Year': years,
        'Starting Balance': start_balance,
        'Contributions': contributions,
        'Growth': growth,
        'Total': total
    })

    return df.iloc[1:]


def calculate_total_starting_balance():
    total = (
        st.session_state.get('roth_ira_start_balance')
        + st.session_state.get('hsa_start_balance')
        + st.session_state.get('roth_401k_start_balance')
        + st.session_state.get('trad_401k_start_balance')
        + st.session_state.get('edu_529_start_balance')
        + st.session_state.get('brokerage_start_balance')
     )
    if st.session_state.get('spousal_enabled', False):
        total += (
            st.session_state.get('spouse_roth_ira_start_balance')
            + st.session_state.get('spouse_hsa_start_balance')
            + st.session_state.get('spouse_roth_401k_start_balance')
            + st.session_state.get('spouse_trad_401k_start_balance')
            + st.session_state.get('spouse_brokerage_start_balance')
        )
    return total


def calculate_annual_contributions_by_account(spouse=False):
    if spouse:
        bonus_amt = get_spouse_bonus_amount()
        salary = st.session_state.get('spouse_salary', 0)
        trad_rate = st.session_state.get('spouse_trad_401k_rate', 0)
        roth_rate = st.session_state.get('spouse_roth_401k_rate', 0)
        match_rate = st.session_state.get('spouse_trad_401k_match_rate', 0)
        return {
            'roth_401k': (roth_rate / 100) * salary + (roth_rate / 100) * bonus_amt,
            'trad_401k': (trad_rate + match_rate) / 100 * salary + (trad_rate / 100) * bonus_amt,
            'hsa': st.session_state.get('spouse_hsa', 0) + st.session_state.get('spouse_hsa_match', 0),
            'roth_ira': st.session_state.get('spouse_roth_ira', 0),
            'brokerage': st.session_state.get('spouse_brokerage', 0),
        }

    bonus_amt = get_bonus_amount()
    annual_contributions = dict()
    annual_contributions['roth_401k'] = (st.session_state.get('roth_401k_rate')/100) * st.session_state.get('salary') + (st.session_state.get('roth_401k_rate')/100) * bonus_amt
    annual_contributions['trad_401k'] = (st.session_state.get('trad_401k_rate') + st.session_state.get('trad_401k_match_rate'))/100 * st.session_state.get('salary') + (st.session_state.get('trad_401k_rate')/100) * bonus_amt
    annual_contributions['hsa'] = st.session_state.get('hsa') + st.session_state.get('hsa_match')
    annual_contributions['roth_ira'] = st.session_state.get('roth_ira')
    annual_contributions['brokerage'] = st.session_state.get('brokerage')
    annual_contributions['edu_529'] = st.session_state.get('edu_529')
    return annual_contributions


def get_expected_returns_by_account(spouse=False):
    keys = SPOUSE_ACCOUNT_KEYS if spouse else ACCOUNT_KEYS
    prefix = 'spouse_' if spouse else ''
    expected_returns = dict()
    for account in keys:
        expected_returns[account] = st.session_state.get(f'{prefix}{account}_expected_return')
    return expected_returns


def get_current_balance_by_account(spouse=False):
    keys = SPOUSE_ACCOUNT_KEYS if spouse else ACCOUNT_KEYS
    prefix = 'spouse_' if spouse else ''
    start_balances = dict()
    for account in keys:
        start_balances[account] = st.session_state.get(f'{prefix}{account}_start_balance')
    return start_balances


def nest_egg_forecast_by_account_df(config_dict: dict, years_to_retirement=None):
    full_df = pd.DataFrame()
    include_529 = st.session_state.get('include_529_in_nest_egg', True)
    if years_to_retirement is None:
        years_to_retirement = st.session_state.get('years_to_retirement', 25)
    for account, details in config_dict.items():
        if account == 'edu_529' and not include_529:
            continue
        if 'edu_529' in account and not include_529:
            continue
        df = calculate_investment(
            details['start_balance'],
            details['contributions'],
            years_to_retirement,
            details['expected_return'],
        )
        df['Account'] = account
        df['Total'] = df['Total'].round(2)
        if df['Total'].max() > 0:
            full_df = pd.concat([full_df,df[['Year','Account','Total','Starting Balance','Contributions','Growth']]])
    return full_df
