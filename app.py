import streamlit as st

from tools.globals import DEFAULTS
from tools.session_data import init_session_data

st.set_page_config(
    page_title="401-OK",
    page_icon="👌",
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items={
        "Report a bug":"https://github.com/M-Barrows/401-ok/issues",
        "About":"""
            Made with 💛 by [Code and Coffee](https://codecoffee.org). I made this entirely for me. If you find use in it, that's a big win!

            I often found myself drafting up what-if scenarios after catching up with my latest personal finance creators. However, that task involved creating new one-off spreadsheets, tweaking it until the monthly takehome amount was acceptable, generating a monthly savings amount, plugging that into various online calculators, going back to the spreadsheet, etc., etc. It was fun to dream but the workflow was exhausting. 

            That's how 401-ok came to be. I just needed a single place to do all of my experimenting. This tool does NOT rival many of the existing tools out there in terms of number of features. But, what it does do is answer the questions for my specific (very simple) situation and provide instant feedback when changes in allocation are made. I don't plan to make big changes to this tool. But, as I have more questions or what-if scenarios that I can't answer, I will look to expand the tool at that time. 

            If you like my work and want to connect, you can find me here: 

            * [Github](https://github.com/M-Barrows/)
            * [LinkedIn](https://www.linkedin.com/in/michaelabarrows/)
            """
    }) 
st.write("# 401-OK! 👌")

init_session_data()
    

for key,value in DEFAULTS.items():
    if key in st.session_state:
        st.session_state[key]=st.session_state[key]
pg = st.navigation({
    "Home": [st.Page('pages/overview/home.py',title="Home",icon="🏠",default=True)],
    "Retirement": [
    # st.Page('pages/retirement/profile.py', title="Overview", icon="🏖"),
    st.Page('pages/retirement/accounts.py', title="Accounts", icon="🏦")
    ]
})
pg.run()
# st.session_state
