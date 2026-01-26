from .globals import (
    ACCOUNT_KEYS,
    STANDARD_DEDUCTION,
    BRACKETS,
    CHILD_TAX_CREDIT,
    MAX_HSA,
    MAX_ROTH_IRA,
    MAX_401K,
)
import streamlit as st
import pandas as pd
from datetime import datetime


def calc_401k_match(savings_rate: float, match: float, limit: float):
    if savings_rate == 0:
        return 0
    if savings_rate < limit:
        return savings_rate * match
    else:
        return match * limit


def calculate_taxable_income(**kwargs):
    salary = kwargs.get("salary", st.session_state["salary"])
    bonus = kwargs.get("bonus", st.session_state["bonus"])
    hsa = kwargs.get("hsa", st.session_state["hsa"])
    donations = kwargs.get("donations", st.session_state["donations"])
    misc_pre_tax_deductions = kwargs.get(
        "misc_pre_tax_deductions", st.session_state["misc_pre_tax_deductions"]
    )
    trad_401k_rate = (
        kwargs.get("trad_401k_rate", st.session_state.get("trad_401k_rate", 0)) / 100
    )
    bonus_amount = bonus / 100 * salary
    st.session_state["taxable_income"] = (
        (salary + bonus_amount)
        - STANDARD_DEDUCTION
        - (trad_401k_rate * (salary + bonus_amount))
        - hsa
        - misc_pre_tax_deductions
        - donations
    )
    return st.session_state["taxable_income"]


def calculate_tax(taxable_income, brackets=BRACKETS):
    """
    Calculate the total tax owed given a salary and tax brackets.

    Parameters:
    taxable_income (float): The income to calculate tax on.
    brackets (list of tuples): Each tuple is (limit, rate), where:
        - limit is the upper bound of that bracket (None for no limit).
        - rate is the tax rate for that bracket (as a decimal, e.g., 0.22 for 22%).

    Returns:
    float: The total tax owed.
    """

    tax = 0.0
    previous_limit = 0.0
    for limit, rate in brackets:
        if limit is None or taxable_income <= limit:
            tax += (taxable_income - previous_limit) * rate
            break
        else:
            tax += (limit - previous_limit) * rate
            previous_limit = limit

    for i in [0.062, 0.0145, st.session_state["state_local_tax"] / 100]:
        # Social Security, Medicare, and State/Local taxes
        tax += taxable_income * i
    return tax


def calc_remaining_salary(roth, hsa, trad_401k, roth_401k):
    extras = (
        (st.session_state["min_net_pay"] * 12)
        - st.session_state["misc_pre_tax_deductions"]
        - st.session_state["misc_post_tax_deductions"]
        - st.session_state["donations"]
        - st.session_state["edu_529"]
    )
    trad_401k_rate = trad_401k / (
        st.session_state["salary"] + st.session_state["bonus_amt"]
    )
    taxable_income = calculate_taxable_income(hsa=hsa, trad_401k_rate=trad_401k_rate)
    income_tax = calculate_tax(taxable_income)
    remaining = (
        st.session_state["salary"]
        - extras
        - income_tax
        - hsa
        - trad_401k
        - roth
        - roth_401k
    )
    return remaining


def compute_net_monthly():
    # Tax base includes salary + bonus for IRS liability
    ti = calculate_taxable_income(
        salary=st.session_state["salary"],
        bonus=st.session_state["bonus"],
        hsa=st.session_state["hsa"],
        donations=st.session_state["donations"],
        misc_pre_tax_deductions=st.session_state["misc_pre_tax_deductions"],
        trad_401k_rate=st.session_state.get("trad_401k_rate", 0),
    )
    st.session_state["income_tax"] = calculate_tax(ti) - (
        CHILD_TAX_CREDIT * st.session_state.get("children", 0)
    )
    pay_periods = st.session_state["pay_periods"]
    # Spread annual amounts across pay periods
    tax_per_period = st.session_state["income_tax"] / pay_periods
    roth_ira_per_period = st.session_state["roth_ira"] / pay_periods
    brokerage_per_period = st.session_state["brokerage"] / pay_periods
    hsa_per_period = st.session_state["hsa"] / pay_periods
    misc_post_per_period = st.session_state["misc_post_tax_deductions"] / pay_periods
    misc_pre_per_period = st.session_state["misc_pre_tax_deductions"] / pay_periods
    donations_per_period = st.session_state.get("donations", 0) / pay_periods

    salary_per_period = st.session_state["salary"] / pay_periods
    edu_529_per_period = st.session_state["edu_529"] / pay_periods
    trad_per_period = (
        (st.session_state["trad_401k_rate"] / 100)
        * st.session_state["salary"]
        / pay_periods
    )
    roth_per_period = (
        (st.session_state["roth_401k_rate"] / 100)
        * st.session_state["salary"]
        / pay_periods
    )

    takehome_per_period = (
        salary_per_period
        - trad_per_period
        - roth_per_period
        - roth_ira_per_period
        - brokerage_per_period
        - hsa_per_period
        - tax_per_period
        - misc_post_per_period
        - misc_pre_per_period
        - donations_per_period
        - edu_529_per_period
    )
    return takehome_per_period * 2  # two pay periods ≈ one month


def optimize_for_foo():
    def maximize_contribution_dollars(max_dollars, apply_fn):
        lo, hi = 0, int(max(0, max_dollars))
        best = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            apply_fn(mid)
            net_monthly = compute_net_monthly()
            if net_monthly >= st.session_state["min_net_pay"]:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        apply_fn(best)
        return best

    # Reset buckets
    st.session_state["hsa"] = 0
    st.session_state["roth_ira"] = 0
    st.session_state["trad_401k_rate"] = 0
    st.session_state["roth_401k_rate"] = 0
    compute_net_monthly()

    SAL = st.session_state["salary"]

    # 1) HSA
    hsa_remaining = max(0, MAX_HSA - st.session_state.get("hsa_match", 0))
    maximize_contribution_dollars(
        hsa_remaining, lambda d: st.session_state.update({"hsa": int(d)})
    )

    # 2) Roth IRA
    maximize_contribution_dollars(
        MAX_ROTH_IRA, lambda d: st.session_state.update({"roth_ira": int(d)})
    )

    # 3) Traditional 401k search in integer percents
    def net_ok_with_trad_percent(pct_int):
        trad_dollars = (pct_int / 100) * SAL
        roth_dollars = (st.session_state["roth_401k_rate"] / 100) * SAL
        if trad_dollars + roth_dollars > MAX_401K:
            return False
        st.session_state["trad_401k_rate"] = pct_int
        nm = compute_net_monthly()
        return nm >= st.session_state["min_net_pay"]

    lo, hi = 0, 25
    best_pct = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if net_ok_with_trad_percent(mid):
            best_pct = mid
            lo = mid + 1
        else:
            hi = mid - 1
    st.session_state["trad_401k_rate"] = best_pct

    # Final sweep with debug
    pct = st.session_state["trad_401k_rate"]
    while pct < 25:
        next_pct = pct + 1
        next_dollars = (next_pct / 100) * SAL
        roth_dollars = (st.session_state["roth_401k_rate"] / 100) * SAL
        total_dollars = next_dollars + roth_dollars
        if total_dollars > MAX_401K:
            break
        st.session_state["trad_401k_rate"] = next_pct
        nm = compute_net_monthly()
        if nm >= st.session_state["min_net_pay"]:
            pct = next_pct
        else:
            st.session_state["trad_401k_rate"] = pct
            break


def calculate_total_savings_dollars():
    trad_401k_dollars = (
        st.session_state.get("trad_401k_rate", 0) / 100
    ) * st.session_state["salary"]
    trad_match_dollars = (
        (st.session_state.get("trad_401k_match_rate", 0))
        / 100
        * st.session_state["salary"]
    )
    roth_401k_dollars = (st.session_state["roth_401k_rate"] / 100) * st.session_state[
        "salary"
    ]
    roth_ira_dollars = st.session_state["roth_ira"]
    hsa_dollars = st.session_state["hsa"]
    hsa_match_dollars = st.session_state.get("hsa_match", 0)
    brokerage_dollars = st.session_state["brokerage"]
    edu_529_dollars = st.session_state.get("edu_529", 0)

    total_savings_dollars = (
        trad_401k_dollars
        + trad_match_dollars
        + roth_401k_dollars
        + roth_ira_dollars
        + hsa_dollars
        + hsa_match_dollars
        + brokerage_dollars
        + edu_529_dollars
    )
    return total_savings_dollars


def calculate_total_takehome_paycheck():
    takehome_paycheck = (
        st.session_state["salary"]
        - (st.session_state["trad_401k_rate"] / 100 * st.session_state["salary"])
        - (st.session_state["roth_401k_rate"] / 100 * st.session_state["salary"])
        - st.session_state["roth_ira"]
        - st.session_state["brokerage"]
        - st.session_state["hsa"]
        - st.session_state["income_tax"]  # tax is still based on salary+bonus
        - st.session_state["misc_post_tax_deductions"]
        - st.session_state["misc_pre_tax_deductions"]
        - st.session_state["donations"]
    ) / st.session_state["pay_periods"]
    return takehome_paycheck


def calculate_investment(
    starting_balance: int,
    annual_contribution,
    years_to_retirement: int = 25,
    growth_rate: int = 8,
):
    """
        Calculate the future value of an investment.

        Parameters:
        starting_balance (int): The initial balance of the investment.
        annual_contribution (int): The amount contributed to the investment each year.
        years_to_retirement (int): The number of years until retirement. Defaults to 25.
        growth_rate (int): The rate at which the investment grows each year. Defaults to 8.

        Returns:
        pandas.DataFrame: A DataFrame containing the year, starting balance, cumulative
    contributions,
                         cumulative growth, and total values for each year.
    """

    # Create a list of years
    this_year = datetime.now().year
    years = range(this_year, this_year + years_to_retirement)

    start_balance = [starting_balance] * len(years)
    contributions = [0] * len(years)
    growth = [0.0] * len(years)
    total = [0.0] * len(years)
    total[0] = starting_balance
    for i in range(1, len(years)):
        contributions[i] = contributions[i - 1] + annual_contribution
        growth[i] = growth[i - 1] + (total[i - 1] * growth_rate / 100)
        total[i] = start_balance[i] + contributions[i] + growth[i]

    # Create a pandas DataFrame from the lists
    df = pd.DataFrame(
        {
            "Year": years,
            "Starting Balance": start_balance,
            "Contributions": contributions,
            "Growth": growth,
            "Total": total,
        }
    )

    return df.iloc[1:]


def calculate_total_starting_balance():
    total = (
        (st.session_state.get("roth_ira_start_balance") or 0)
        + (st.session_state.get("hsa_start_balance") or 0)
        + (st.session_state.get("roth_401k_start_balance") or 0)
        + (st.session_state.get("trad_401k_start_balance") or 0)
        + (st.session_state.get("edu_529_start_balance") or 0)
        + (st.session_state.get("brokerage_start_balance") or 0)
    )
    return total


def calculate_annual_contributions_by_account():
    annual_contributions = dict()
    annual_contributions["roth_401k"] = (
        (st.session_state.get("roth_401k_rate") or 0) / 100
    ) * (st.session_state.get("salary") or 0)
    annual_contributions["trad_401k"] = (
        (
            (st.session_state.get("trad_401k_rate") or 0)
            + (st.session_state.get("trad_401k_match_rate") or 0)
        )
        / 100
        * (st.session_state.get("salary") or 0)
    )
    annual_contributions["hsa"] = (st.session_state.get("hsa") or 0) + (
        st.session_state.get("hsa_match") or 0
    )
    annual_contributions["roth_ira"] = st.session_state.get("roth_ira") or 0
    annual_contributions["brokerage"] = st.session_state.get("brokerage") or 0
    annual_contributions["edu_529"] = st.session_state.get("edu_529") or 0
    return annual_contributions


def get_expected_returns_by_account():
    expected_returns = dict()
    for account in ACCOUNT_KEYS:
        expected_returns[account] = st.session_state.get(f"{account}_expected_return")
    return expected_returns


def get_current_balance_by_account():
    start_balances = dict()
    for account in ACCOUNT_KEYS:
        start_balances[account] = st.session_state.get(f"{account}_start_balance")
    return start_balances


def get_tax_bucket_breakdown():
    """
    Group account balances by tax treatment.

    Returns:
    dict: Dictionary with tax buckets as keys and total balances as values
    """
    balances = get_current_balance_by_account()

    tax_buckets = {"Tax-Free": 0, "Tax-Deferred": 0, "After-Tax": 0}

    # Tax-Free accounts (Roth IRA, Roth 401k, HSA)
    tax_buckets["Tax-Free"] += balances.get("roth_ira", 0)
    tax_buckets["Tax-Free"] += balances.get("roth_401k", 0)
    tax_buckets["Tax-Free"] += balances.get("hsa", 0)

    # Tax-Deferred accounts (Traditional 401k, 529 Education)
    tax_buckets["Tax-Deferred"] += balances.get("trad_401k", 0)
    tax_buckets["Tax-Deferred"] += balances.get("edu_529", 0)

    # After-Tax accounts (Brokerage)
    tax_buckets["After-Tax"] += balances.get("brokerage", 0)

    return tax_buckets


def get_tax_bucket_forecast_df():
    """
    Calculate tax bucket breakdown over time using the same forecast logic as individual accounts.

    Returns:
    pandas.DataFrame: DataFrame with years and tax bucket balances over time
    """
    from datetime import datetime

    # Get current tax bucket breakdown
    current_tax_buckets = get_tax_bucket_breakdown()

    # Create account config for tax buckets
    tax_bucket_config = {
        "Tax-Free": {
            "start_balance": current_tax_buckets["Tax-Free"],
            "contributions": 0,  # Will be calculated below
            "expected_return": 8,  # Default return rate
        },
        "Tax-Deferred": {
            "start_balance": current_tax_buckets["Tax-Deferred"],
            "contributions": 0,  # Will be calculated below
            "expected_return": 8,  # Default return rate
        },
        "After-Tax": {
            "start_balance": current_tax_buckets["After-Tax"],
            "contributions": 0,  # Will be calculated below
            "expected_return": 8,  # Default return rate
        },
    }

    # Calculate annual contributions by tax bucket
    contributions = calculate_annual_contributions_by_account()

    # Tax-Free contributions (Roth IRA, Roth 401k, HSA)
    tax_bucket_config["Tax-Free"]["contributions"] = (
        contributions.get("roth_ira", 0)
        + contributions.get("roth_401k", 0)
        + contributions.get("hsa", 0)
    )

    # Tax-Deferred contributions (Traditional 401k, 529 Education)
    tax_bucket_config["Tax-Deferred"]["contributions"] = contributions.get(
        "trad_401k", 0
    ) + contributions.get("edu_529", 0)

    # After-Tax contributions (Brokerage)
    tax_bucket_config["After-Tax"]["contributions"] = contributions.get("brokerage", 0)

    # Generate forecast for each tax bucket
    full_df = pd.DataFrame()

    for tax_bucket, config in tax_bucket_config.items():
        if config["start_balance"] > 0 or config["contributions"] > 0:
            df = calculate_investment(
                config["start_balance"],
                config["contributions"],
                st.session_state.get("years_to_retirement", 25),
                config["expected_return"],
            )
            df["Tax Bucket"] = tax_bucket
            df["Total"] = df["Total"].round(2)
            full_df = pd.concat([full_df, df[["Year", "Tax Bucket", "Total"]]])

    # Pivot to create stacked bar chart format
    if not full_df.empty:
        pivot_df = full_df.pivot(
            index="Year", columns="Tax Bucket", values="Total"
        ).fillna(0)
        return pivot_df.reset_index()
    else:
        return pd.DataFrame()


def nest_egg_forecast_by_account_df(config_dict: dict):
    full_df = pd.DataFrame()
    for account, details in config_dict.items():
        df = calculate_investment(
            details["start_balance"],
            details["contributions"],
            st.session_state.get("years_to_retirement", 25),
            details["expected_return"],
        )
        df["Account"] = account
        df["Total"] = df["Total"].round(2)
        if df["Total"].max() > 0:
            full_df = pd.concat(
                [
                    full_df,
                    df[
                        [
                            "Year",
                            "Account",
                            "Total",
                            "Starting Balance",
                            "Contributions",
                            "Growth",
                        ]
                    ],
                ]
            )
    return full_df
