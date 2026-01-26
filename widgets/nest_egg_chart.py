from tools.globals import ACCOUNT_KEYS
from tools.helper_funcs import (
    calculate_annual_contributions_by_account,
    calculate_total_savings_dollars,
    calculate_investment,
    calculate_total_starting_balance,
    get_current_balance_by_account,
    get_expected_returns_by_account,
    nest_egg_forecast_by_account_df,
    get_tax_bucket_breakdown,
    get_tax_bucket_forecast_df,
)
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
    retirement_outlook = st.expander("📈 Forecast View", expanded=True)

    with retirement_outlook:
        c_retirement_journey_chart, c_retirement_journey_commentary = st.columns([2, 1])

        with c_retirement_journey_chart:
            t_contributions, t_account, t_tax_bucket = st.tabs(
                ["Contributions", "Account", "Tax Bucket"]
            )
            contributions = calculate_annual_contributions_by_account()
            expected_returns = get_expected_returns_by_account()
            starting_balance = get_current_balance_by_account()
            config_dict = dict()
            for account in ACCOUNT_KEYS:
                config_dict.update(
                    {
                        account: {
                            "expected_return": expected_returns[account],
                            "start_balance": starting_balance[account],
                            "contributions": contributions[account],
                        }
                    }
                )

            chart_df = nest_egg_forecast_by_account_df(config_dict)
            chart_df["Account"] = chart_df.apply(
                lambda X: X.Account.replace("_", " ").title(), axis=1
            )

        with t_contributions:
            chart_df_grouped = chart_df.groupby(["Year"]).sum().reset_index()
            st.bar_chart(
                data=chart_df_grouped,
                x="Year",
                y=["Starting Balance", "Contributions", "Growth"],
                sort=False,
            )

        with t_account:
            st.bar_chart(
                data=chart_df, x="Year", y="Total", color="Account", sort="Total"
            )

        with t_tax_bucket:
            tax_forecast_df = get_tax_bucket_forecast_df()

            if not tax_forecast_df.empty:
                # Create stacked bar chart with tax bucket columns
                tax_bucket_columns = [
                    col for col in tax_forecast_df.columns if col != "Year"
                ]
                st.bar_chart(
                    data=tax_forecast_df,
                    x="Year",
                    y=tax_bucket_columns,
                    stack=True,
                    sort=False,
                )
            else:
                st.info(
                    "No account balances found. Add balances to see tax bucket breakdown over time."
                )

        with c_retirement_journey_commentary:
            st.number_input(
                "Years Until Retirement",
                min_value=1,
                max_value=50,
                key="years_to_retirement",
            )

            # Get forecast data for tax buckets to show ending balances
            tax_forecast_df = get_tax_bucket_forecast_df()

            if not tax_forecast_df.empty:
                # Align displayed totals with the portfolio total for the last year
                bucket_columns = [
                    col for col in tax_forecast_df.columns if col != "Year"
                ]
                last_row = tax_forecast_df.iloc[-1]
                last_portfolio_total = chart_df.groupby("Year").sum().iloc[-1]["Total"]
                sum_buckets_last = last_row[bucket_columns].sum()
                scale = (last_portfolio_total or 0) / (sum_buckets_last or 1)

                st.write("**Ending Balances** \n ")
                st.write(f"Total: ${'{:,.0f}'.format(last_portfolio_total)}")

                st.write("")
                st.write("**Tax Bucket Totals:**")

                for tax_bucket in ["Tax-Free", "Tax-Deferred", "After-Tax"]:
                    if tax_bucket in tax_forecast_df.columns:
                        bucket_end = last_row[tax_bucket]
                        val = bucket_end * scale
                        if val > 0:
                            percentage = (val / (last_portfolio_total or 1)) * 100
                            st.write(
                                f"{tax_bucket}: ${'{:,.0f}'.format(val)} ({percentage:.1f}%)"
                            )
            else:
                # Fallback to current tax bucket breakdown if no forecast data
                total_ending_balance = chart_df.groupby("Year").sum().iloc[-1]["Total"]

                st.write("**Ending Balances** \n ")
                st.write(f"Total: ${'{:,.0f}'.format(total_ending_balance)}")

                # Show current tax bucket breakdown
                st.write("")
                st.write("**Tax Bucket Totals:**")
                tax_buckets = get_tax_bucket_breakdown()

                total_tax_balance = sum(tax_buckets.values())
                if total_tax_balance > 0:
                    for tax_bucket, balance in tax_buckets.items():
                        if balance > 0:
                            percentage = (balance / total_tax_balance) * 100
                            st.write(
                                f"{tax_bucket}: ${'{:,.0f}'.format(balance)} ({percentage:.1f}%)"
                            )

            # st.number_input("Initial Retirement Balance",min_value=0,key="initial_retirement_balance")
            # st.number_input("Expected Return %",min_value=1.0,max_value=50.0,key="expected_investment_return",format="%0.1f")
