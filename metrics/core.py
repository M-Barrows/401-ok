import streamlit as st

def paycheck_metric():
    return st.metric("💸 Your Paycheck", 
      "~ $"+'{:,.0f}'.format(6300.00),
      "~ $"+'{:,.0f}'.format(6300*12)+' Yearly',
      border=True,
      height="stretch",
      delta_color="off",
      delta_arrow="off")

def savings_rate_metric(): 
    return st.metric("📈 Savings Rate",
              '{:,.2f}%'.format(0.25*100),
              border=True,
              height="stretch")
def savings_amt_metric():
    return st.metric(
          "🏦 Total Savings",
          "~ $"+'{:,.0f}'.format(round(45_000)),
          "$"+'{:,.0f}'.format(round(45_000/12))+" Monthly",
          border=True,
          delta_arrow="off",
          delta_color="off"
    )
def nest_egg_metric():
    return st.metric(
          "📈 Projected Nest Egg",
          "~ $"+'{:,.0f}'.format(round(4_500_000)),
          "$"+'{:,.0f}'.format(round(4_500_000*0.047))+" Annually",
          border=True,
          delta_arrow="off",
          delta_color="off"
    )
__all__ = ['paycheck_metric','savings_rate_metric','savings_amt_metric','nest_egg_metric']
