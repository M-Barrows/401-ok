import streamlit as st

c_1, c_2, c_3 = st.columns(3)

with c_1: 
    st.number_input("Inflation Rate", value = 3.0)
    st.number_input("Growth Rate", value= 7.0)
    st.number_input("Social Security Claim Age", value=70)
with c_2:
    from streamlit_multi_slider import multi_slider
    values, ranges = multi_slider(
        label="Retirement Phases",
        bounds=(50, 100),
        num_points=3,
        labels=["Working", "Go-Go", "Slow-Go", "No-Go"],
        default_values=[55, 70, 80],
        min_spacing=5,
    )
