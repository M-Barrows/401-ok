import streamlit as st
import pandas as pd
from metrics.core import nest_egg_metric, paycheck_metric, savings_amt_metric, savings_rate_metric
from widgets.nest_egg_chart import nest_egg_forecast_chart

nest_egg_forecast_chart()
