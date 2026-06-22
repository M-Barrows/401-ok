from tools.globals import ACCOUNT_KEYS
from tools.helper_funcs import calculate_annual_contributions_by_account, calculate_total_savings_dollars, calculate_investment, calculate_total_starting_balance, get_current_balance_by_account, get_expected_returns_by_account, nest_egg_forecast_by_account_df
import streamlit as st
import pandas as pd


def nest_egg_forecast_chart():
    retirement_outlook = st.expander("📈 Forecast View", expanded=True)

    with retirement_outlook:
        c_retirement_journey_chart, c_retirement_journey_commentary = st.columns([2, 1])

        spousal = st.session_state.get('spousal_enabled', False)
        primary_name = st.session_state.get('primary_name', 'Primary')
        spouse_name = st.session_state.get('spouse_name', 'Spouse')

        contributions = calculate_annual_contributions_by_account()
        primary_years = st.session_state.get('years_to_retirement', 25)
        spouse_years = st.session_state.get('spouse_years_to_retirement', 25) if spousal else 25
        max_years = max(primary_years, spouse_years)

        primary_df = nest_egg_forecast_by_account_df({
            account: {
                'start_balance': get_current_balance_by_account()[account],
                'contributions': contributions.get(account, 0),
                'expected_return': get_expected_returns_by_account()[account],
            }
            for account in ACCOUNT_KEYS
        })

        spouse_df = pd.DataFrame()
        spouse_contributions = {}
        if spousal:
            spouse_contributions = calculate_annual_contributions_by_account(spouse=True)
            spouse_df = nest_egg_forecast_by_account_df({
                account: {
                    'start_balance': get_current_balance_by_account(spouse=True)[account],
                    'contributions': spouse_contributions.get(account, 0),
                    'expected_return': get_expected_returns_by_account(spouse=True)[account],
                }
                for account in ['roth_ira', 'hsa', 'roth_401k', 'trad_401k', 'brokerage']
            }, years_to_retirement=spouse_years)

        with c_retirement_journey_chart:
            if spousal:
                combined = st.checkbox("Show combined (MFJ)", value=True, key="forecast_combined_view")
            else:
                combined = True

            charts = []
            if combined:
                if not primary_df.empty and not spouse_df.empty:
                    p2 = nest_egg_forecast_by_account_df({
                        account: {
                            'start_balance': get_current_balance_by_account()[account],
                            'contributions': contributions.get(account, 0),
                            'expected_return': get_expected_returns_by_account()[account],
                        }
                        for account in ACCOUNT_KEYS
                    }, years_to_retirement=max_years)
                    s2 = nest_egg_forecast_by_account_df({
                        account: {
                            'start_balance': get_current_balance_by_account(spouse=True)[account],
                            'contributions': spouse_contributions.get(account, 0),
                            'expected_return': get_expected_returns_by_account(spouse=True)[account],
                        }
                        for account in ['roth_ira', 'hsa', 'roth_401k', 'trad_401k', 'brokerage']
                    }, years_to_retirement=max_years)
                    chart_df = p2._append(s2, ignore_index=True)
                elif not primary_df.empty:
                    chart_df = primary_df
                elif not spouse_df.empty:
                    chart_df = spouse_df
                else:
                    chart_df = pd.DataFrame()
                charts = [("Combined", chart_df)]
            else:
                if not primary_df.empty:
                    charts.append((primary_name, primary_df))
                if not spouse_df.empty:
                    charts.append((spouse_name, spouse_df))

            if charts:
                t_contributions, t_account = st.tabs(['Contributions', 'Account'])

                with t_contributions:
                    for label, df in charts:
                        if not df.empty:
                            if len(charts) > 1:
                                st.subheader(label)
                            chart_df_grouped = df.groupby(['Year'])[['Starting Balance', 'Contributions', 'Growth']].sum().reset_index()
                            st.bar_chart(data=chart_df_grouped, x='Year', y=['Starting Balance', 'Contributions', 'Growth'], sort=False)

                with t_account:
                    for label, df in charts:
                        if not df.empty:
                            if len(charts) > 1:
                                st.subheader(label)
                            df = df.copy()
                            df['Account'] = df['Account'].apply(lambda X: X.replace('_', ' ').title())
                            st.bar_chart(data=df, x='Year', y='Total', color='Account', sort='Total')

        with c_retirement_journey_commentary:
            if combined and not chart_df.empty:
                st.write(f"**Ending Balance: ${'{:,.0f}'.format(chart_df.groupby('Year').sum().iloc[-1]['Total'])}**")
            elif not combined:
                for label, df in charts:
                    if not df.empty:
                        final_val = df.groupby('Year').sum().iloc[-1]['Total']
                        st.write(f"**{label}: ${'{:,.0f}'.format(final_val)}**")

            if combined and not chart_df.empty:
                primary_age = st.session_state.get('primary_age', 35)
                retirement_age_primary = primary_age + primary_years
                if spousal:
                    spouse_age = st.session_state.get('spouse_age', 35)
                    retirement_age_spouse = spouse_age + spouse_years
                    st.write(f"Retirement ages: {primary_name} {retirement_age_primary}, {spouse_name} {retirement_age_spouse}")
                else:
                    st.write(f"Retirement age: {retirement_age_primary}")

            st.number_input(f"{primary_name}'s Years Until Retirement", min_value=1, max_value=50, key="years_to_retirement")
            if spousal:
                st.number_input(f"{spouse_name}'s Years Until Retirement", min_value=1, max_value=50, key="spouse_years_to_retirement")
