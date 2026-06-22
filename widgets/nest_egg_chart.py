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

            # Recompute both with same year range for proper combining
            p2 = nest_egg_forecast_by_account_df({
                account: {
                    'start_balance': get_current_balance_by_account()[account],
                    'contributions': contributions.get(account, 0),
                    'expected_return': get_expected_returns_by_account()[account],
                }
                for account in ACCOUNT_KEYS
            }, years_to_retirement=max_years) if spousal else primary_df

            s2 = nest_egg_forecast_by_account_df({
                account: {
                    'start_balance': get_current_balance_by_account(spouse=True)[account],
                    'contributions': spouse_contributions.get(account, 0),
                    'expected_return': get_expected_returns_by_account(spouse=True)[account],
                }
                for account in ['roth_ira', 'hsa', 'roth_401k', 'trad_401k', 'brokerage']
            }, years_to_retirement=max_years) if spousal else pd.DataFrame()

            yearly = pd.DataFrame()

            # Build chart data: (label, yearly_agg_df, account_detail_df)
            chart_sets = []
            if combined:
                if not p2.empty and not s2.empty:
                    p_sum = p2.groupby('Year')[['Starting Balance', 'Contributions', 'Growth']].sum()
                    s_sum = s2.groupby('Year')[['Starting Balance', 'Contributions', 'Growth']].sum()
                    yearly = p_sum.add(s_sum, fill_value=0).reset_index()
                    detail = pd.concat([p2, s2], ignore_index=True)
                elif not p2.empty:
                    yearly = p2.groupby('Year')[['Starting Balance', 'Contributions', 'Growth']].sum().reset_index()
                    detail = p2
                elif not s2.empty:
                    yearly = s2.groupby('Year')[['Starting Balance', 'Contributions', 'Growth']].sum().reset_index()
                    detail = s2
                else:
                    yearly = pd.DataFrame()
                    detail = pd.DataFrame()
                chart_sets = [("Combined", yearly, detail)]
            else:
                if not primary_df.empty:
                    p_yearly = primary_df.groupby('Year')[['Starting Balance', 'Contributions', 'Growth']].sum().reset_index()
                    chart_sets.append((primary_name, p_yearly, primary_df))
                if not spouse_df.empty:
                    s_yearly = spouse_df.groupby('Year')[['Starting Balance', 'Contributions', 'Growth']].sum().reset_index()
                    chart_sets.append((spouse_name, s_yearly, spouse_df))

            if chart_sets:
                t_contributions, t_account = st.tabs(['Contributions', 'Account'])

                with t_contributions:
                    for label, yearly, _ in chart_sets:
                        if not yearly.empty:
                            if len(chart_sets) > 1:
                                st.subheader(label)
                            clean = pd.DataFrame({
                                'Year': yearly['Year'].values,
                                'Starting Balance': yearly['Starting Balance'].values.astype(float),
                                'Contributions': yearly['Contributions'].values.astype(float),
                                'Growth': yearly['Growth'].values.astype(float),
                            })
                            st.bar_chart(data=clean.set_index('Year'))

                with t_account:
                    for label, _, detail in chart_sets:
                        if not detail.empty:
                            if len(chart_sets) > 1:
                                st.subheader(label)
                            plot_df = detail.copy()
                            plot_df['Account'] = plot_df['Account'].apply(lambda X: X.replace('_', ' ').title())
                            grouped = plot_df.groupby(['Year', 'Account'])['Total'].sum().reset_index()
                            pivot = grouped.pivot_table(index='Year', columns='Account', values='Total', aggfunc='sum').fillna(0)
                            st.bar_chart(data=pivot)

        with c_retirement_journey_commentary:
            if combined and not yearly.empty:
                total_row = yearly[['Starting Balance', 'Contributions', 'Growth']].sum(axis=1)
                st.write(f"**Ending Balance: ${'{:,.0f}'.format(total_row.iloc[-1])}**")
            elif not combined:
                for label, ydf, _ in chart_sets:
                    if not ydf.empty:
                        total_row = ydf[['Starting Balance', 'Contributions', 'Growth']].sum(axis=1)
                        st.write(f"**{label}: ${'{:,.0f}'.format(total_row.iloc[-1])}**")

            if combined and not yearly.empty:
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
