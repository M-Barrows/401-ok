import streamlit as st
from metrics.core import nest_egg_metric, paycheck_metric, savings_amt_metric, savings_rate_metric
from widgets.nest_egg_chart import nest_egg_forecast_chart
from widgets.settings_expander import settings_container

c_metrics, c_settings = st.columns(2)

with c_settings: 
    settings_container()

with c_metrics:
    c_paycheck, c_save_rate = st.columns(2)
    c_save_amt, c_nest_egg_forecast = st.columns(2)
    nest_egg_forecast_chart()


with c_paycheck:
    paycheck_metric()
with c_save_rate:
    savings_rate_metric()
with c_save_amt:
    savings_amt_metric()
with c_nest_egg_forecast:
    nest_egg_metric()

st.session_state    
