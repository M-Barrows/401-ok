import streamlit as st
from tools.globals import MAX_HSA, MAX_401K, MAX_ROTH_IRA, ROTH_IRA_PHASE_OUT_SINGLE, ROTH_IRA_PHASE_OUT_JOINT, ROTH_IRA_CATCHUP
from tools.helper_funcs import get_effective_magi, calculate_roth_ira_max
import yaml
import time


def update_config_from_file():
    uploaded = st.session_state.get('config_file')
    if uploaded is not None:
        try:
            file_content = uploaded.getvalue().decode('utf-8')
            data = yaml.safe_load(file_content)
            if not isinstance(data, dict):
                return
            st.session_state.hsa = data.get('hsa',st.session_state.hsa)
            st.session_state.hsa_match = data.get('hsa_match',0)
            st.session_state.roth_ira = data.get('roth_ira',0)
            st.session_state.trad_401k_rate = data.get('trad_401k_rate',0)
            st.session_state.roth_401k_rate = data.get('roth_401k_rate',0)
            st.session_state.salary = data.get('salary',100)
            st.session_state.bonus = data.get('bonus', 7.5)
            st.session_state.min_net_pay = data.get('min_net_pay',0)
            st.session_state.misc_pre_tax_deductions = data.get('misc_pre_tax_deductions',0)
            st.session_state.misc_post_tax_deductions = data.get('misc_post_tax_deductions',0)
            st.session_state.brokerage = data.get('brokerage',0)
            st.session_state.state_local_tax = data.get('state_local_tax',0)
            st.session_state.children = data.get('children',0)
            st.session_state.donations = data.get('donations', 1700)
            st.session_state.pay_periods = data.get('pay_periods',0)
            st.session_state.years_to_retirement = data.get('years_to_retirement',25)
            st.session_state.roth_ira_start_balance =data.get('roth_ira_start_balance',0)
            st.session_state.roth_ira_expected_return =data.get('roth_ira_expected_return',0)
            st.session_state.hsa_start_balance =data.get('hsa_start_balance',0)
            st.session_state.hsa_expected_return =data.get('hsa_expected_return',0)
            st.session_state.roth_401k_start_balance =data.get('roth_401k_start_balance',0)
            st.session_state.roth_401k_expected_return =data.get('roth_401k_expected_return',0)
            st.session_state.trad_401k_start_balance =data.get('trad_401k_start_balance',0)
            st.session_state.trad_401k_expected_return =data.get('trad_401k_expected_return',0)
            st.session_state.edu_529_start_balance =data.get('edu_529_start_balance',0)
            st.session_state.edu_529_expected_return =data.get('edu_529_expected_return',0)
            st.session_state.brokerage_start_balance =data.get('brokerage_start_balance',0)
            st.session_state.brokerage_expected_return = data.get('brokerage_expected_return', 8)

            st.session_state.edu_529 = data.get('edu_529', 3600)
            st.session_state.include_529_in_nest_egg = data.get('include_529_in_nest_egg', True)

            spousal_cfg = data.get('spousal_enabled', False)
            filing_jointly = data.get('filing_jointly', True) if spousal_cfg else True
            st.session_state['filing_jointly'] = filing_jointly
            st.session_state['filing_status_pill'] = "Single" if not spousal_cfg else ("MFJ" if filing_jointly else "MFS")

            st.session_state.spousal_enabled = data.get('spousal_enabled', False)
            st.session_state.primary_name = data.get('primary_name', 'Spouse1')
            st.session_state.spouse_name = data.get('spouse_name', 'Spouse2')
            st.session_state.primary_age = data.get('primary_age', 30)
            st.session_state.spouse_age = data.get('spouse_age', 30)
            st.session_state.filing_jointly = data.get('filing_jointly', True)
            st.session_state.spouse_salary = data.get('spouse_salary', 0)
            st.session_state.spouse_bonus = data.get('spouse_bonus', 7.5)
            st.session_state.spouse_min_net_pay = data.get('spouse_min_net_pay', 0)
            st.session_state.spouse_trad_401k_rate = data.get('spouse_trad_401k_rate', 0)
            st.session_state.spouse_trad_401k_match_rate = data.get('spouse_trad_401k_match_rate', 0)
            st.session_state.spouse_roth_401k_rate = data.get('spouse_roth_401k_rate', 0)
            st.session_state.spouse_hsa = data.get('spouse_hsa', 0)
            st.session_state.spouse_hsa_match = data.get('spouse_hsa_match', 0)
            st.session_state.spouse_roth_ira = data.get('spouse_roth_ira', 0)
            st.session_state.spouse_brokerage = data.get('spouse_brokerage', 0)
            st.session_state.spouse_misc_pre_tax_deductions = data.get('spouse_misc_pre_tax_deductions', 0)
            st.session_state.spouse_misc_post_tax_deductions = data.get('spouse_misc_post_tax_deductions', 0)
            st.session_state.spouse_donations = data.get('spouse_donations', 0)
            st.session_state.spouse_roth_ira_start_balance = data.get('spouse_roth_ira_start_balance', 0)
            st.session_state.spouse_roth_ira_expected_return = data.get('spouse_roth_ira_expected_return', 8)
            st.session_state.spouse_hsa_start_balance = data.get('spouse_hsa_start_balance', 0)
            st.session_state.spouse_hsa_expected_return = data.get('spouse_hsa_expected_return', 8)
            st.session_state.spouse_roth_401k_start_balance = data.get('spouse_roth_401k_start_balance', 0)
            st.session_state.spouse_roth_401k_expected_return = data.get('spouse_roth_401k_expected_return', 8)
            st.session_state.spouse_trad_401k_start_balance = data.get('spouse_trad_401k_start_balance', 0)
            st.session_state.spouse_trad_401k_expected_return = data.get('spouse_trad_401k_expected_return', 8)
            st.session_state.spouse_brokerage_start_balance = data.get('spouse_brokerage_start_balance', 0)
            st.session_state.spouse_brokerage_expected_return = data.get('spouse_brokerage_expected_return', 8)
            st.session_state.spouse_years_to_retirement = data.get('spouse_years_to_retirement', 25)
        except Exception:
            st.toast("Failed to load config file", icon="⚠️")


def settings_container():
    file_upload_help = f"""
        Please upload a yaml file with any of the following parameters to auto-apply settings. You can copy this and paste it in the file to get a head start.

        > ⚠️For now, this only works on the first time you upload a file. This is a known bug. 
        ```yaml
        hsa: {st.session_state.get('hsa',0)}          # int annual amount
        hsa_match: {st.session_state.get('hsa_match',0)}     # int annual amount
        roth_ira: {st.session_state.get('roth_ira',0)}       # int annual amount
        trad_401k_rate: {st.session_state.get('trad_401k_rate',0)}  # int percent
        roth_401k_rate: {st.session_state.get('roth_401k_rate',0)}  # int percent
        salary: {st.session_state.get('salary',0)}            # int annual amount
        bonus: {st.session_state.get('bonus', 7.5)}           # float percent
        min_net_pay: {st.session_state.get('min_net_pay',0)}      # int monthly
        misc_pre_tax_deductions: {st.session_state.get('misc_pre_tax_deductions',0)}  # int annual
        misc_post_tax_deductions: {st.session_state.get('misc_post_tax_deductions',0)} # int annual
        brokerage: {st.session_state.get('brokerage',0)}          # int annual
        state_local_tax: {st.session_state.get('state_local_tax',0)}  # float percent
        children: {st.session_state.get('children',0)}            # int
        donations: {st.session_state.get('donations', 1700)}      # int annual
        pay_periods: {st.session_state.get('pay_periods',0)}      # int
        years_to_retirement: {st.session_state.get('years_to_retirement',0)}  # int
        edu_529: {st.session_state.get('edu_529', 3600)}          # int annual
        include_529_in_nest_egg: {st.session_state.get('include_529_in_nest_egg', True)}  # bool

        # Spouse settings (only used when spousal_enabled is True)
        spousal_enabled: {st.session_state.get('spousal_enabled', False)}
        primary_name: {st.session_state.get('primary_name', 'Spouse1')}
        spouse_name: {st.session_state.get('spouse_name', 'Spouse2')}
        primary_age: {st.session_state.get('primary_age', 35)}    # int
        spouse_age: {st.session_state.get('spouse_age', 35)}      # int
        spouse_salary: {st.session_state.get('spouse_salary', 0)}     # int annual
        spouse_bonus: {st.session_state.get('spouse_bonus', 7.5)}    # float percent
        spouse_min_net_pay: {st.session_state.get('spouse_min_net_pay', 0)}  # int monthly
        spouse_trad_401k_rate: {st.session_state.get('spouse_trad_401k_rate', 0)}  # int percent
        spouse_trad_401k_match_rate: {st.session_state.get('spouse_trad_401k_match_rate', 0)}  # int percent
        spouse_roth_401k_rate: {st.session_state.get('spouse_roth_401k_rate', 0)}  # int percent
        spouse_hsa: {st.session_state.get('spouse_hsa', 0)}       # int annual
        spouse_hsa_match: {st.session_state.get('spouse_hsa_match', 0)}  # int annual
        spouse_roth_ira: {st.session_state.get('spouse_roth_ira', 0)}  # int annual
        spouse_brokerage: {st.session_state.get('spouse_brokerage', 0)}  # int annual
        spouse_misc_pre_tax_deductions: {st.session_state.get('spouse_misc_pre_tax_deductions', 0)}
        spouse_misc_post_tax_deductions: {st.session_state.get('spouse_misc_post_tax_deductions', 0)}
        spouse_donations: {st.session_state.get('spouse_donations', 0)}  # int annual
        spouse_roth_ira_start_balance: {st.session_state.get('spouse_roth_ira_start_balance', 0)}
        spouse_hsa_start_balance: {st.session_state.get('spouse_hsa_start_balance', 0)}
        spouse_roth_401k_start_balance: {st.session_state.get('spouse_roth_401k_start_balance', 0)}
        spouse_trad_401k_start_balance: {st.session_state.get('spouse_trad_401k_start_balance', 0)}
        spouse_brokerage_start_balance: {st.session_state.get('spouse_brokerage_start_balance', 0)}
        spouse_years_to_retirement: {st.session_state.get('spouse_years_to_retirement', 25)}    # int
        ```
        """
    max401k_perc = int((MAX_401K*100)/(st.session_state['salary']*100)*100)

    errors = st.container()
    settings_container = st.expander("🔧 Settings",expanded=True)

    with settings_container:
        if st.session_state.get('spousal_enabled', False):
            st.session_state['filing_status_pill'] = "MFJ" if st.session_state.get('filing_jointly', True) else "MFS"
        elif 'filing_status_pill' not in st.session_state:
            st.session_state['filing_status_pill'] = "Single"
        filing = st.pills(
            "Filing Status",
            options=["Single", "MFJ", "MFS"],
            default=st.session_state['filing_status_pill'],
            key="filing_status_pill",
            selection_mode="single",
        )
        if filing is not None:
            st.session_state['spousal_enabled'] = filing != "Single"
            st.session_state['filing_jointly'] = filing == "MFJ"

        if st.session_state.get('spousal_enabled', False):
            c_name1, c_name2 = st.columns(2)
            with c_name1:
                st.text_input("Primary Person Name", key="primary_name")
            with c_name2:
                st.text_input("Spouse Person Name", key="spouse_name")
            c_age1, c_age2 = st.columns(2)
            with c_age1:
                st.number_input(f"{st.session_state.get('primary_name', 'Spouse1')}'s Age",
                                18, 80, key='primary_age')
            with c_age2:
                st.number_input(f"{st.session_state.get('spouse_name', 'Spouse2')}'s Age",
                                18, 80, key='spouse_age')

        c_salary, c_pre_tax, c_after_tax, c_misc, c_config = st.tabs(["Salary","Pre-Tax","After Tax","Misc","Config"])

    with c_config:
        c_up_config, c_down_config = st.columns([2,1])

    with c_up_config:
        config_file = st.file_uploader("Upload Config",type=['yaml','yml'],help=file_upload_help,key='config_file',on_change=update_config_from_file)

    with c_salary:
        salary = st.number_input("Annual Salary",min_value=100,step=100, key='salary')
        pay_periods = st.number_input("Pay Periods Per Year",1,52, value=26,key="pay_periods")
        bonus = st.number_input("Annual Bonus %",0.0,15.0, value=7.5, key='bonus')
        min_net_pay = st.number_input("Minimum Allowed Net Monthly Pay",0, key='min_net_pay')
        st.session_state['bonus_amt'] = bonus/100*salary
        st.session_state['total_salary'] = salary + st.session_state['bonus_amt']

        if st.session_state.get('spousal_enabled', False):
            with st.expander(f"{st.session_state.get('spouse_name', 'Spouse2')}'s Salary"):
                st.number_input("Annual Salary", min_value=0, step=100, key='spouse_salary')
                st.number_input("Annual Bonus %", 0.0, 15.0, value=7.5, key='spouse_bonus')
                st.number_input("Minimum Allowed Net Monthly Pay", 0, key='spouse_min_net_pay')
                st.session_state['spouse_bonus_amt'] = st.session_state['spouse_bonus'] / 100 * st.session_state['spouse_salary']

    with c_pre_tax:
        trad_401k_rate = st.slider("401k Savings Rate", 0, max401k_perc, value=min(max401k_perc, st.session_state.get('trad_401k_rate', 0)), key="trad_401k_rate")
        st.number_input("401k Match Rate",key="trad_401k_match_rate")
        hsa = st.number_input("Annual HSA contributions", 0,MAX_HSA,key='hsa')
        hsa_match = st.number_input("Annual HSA employer match", 0,MAX_HSA,value= 1_000,key='hsa_match')
        if (hsa + hsa_match) > MAX_HSA:
            with errors:
                st.error("HSA contributions exceed allowed maximum")

        if st.session_state.get('spousal_enabled', False):
            with st.expander(f"{st.session_state.get('spouse_name', 'Spouse2')}'s Pre-Tax"):
                spouse_sal = st.session_state.get('spouse_salary', 0)
                sp_max401k_perc = int((MAX_401K * 100) / (spouse_sal * 100) * 100) if spouse_sal > 0 else 0
                st.slider("401k Savings Rate", 0, max(sp_max401k_perc, 1), key='spouse_trad_401k_rate')
                st.number_input("401k Match Rate", key='spouse_trad_401k_match_rate')
                st.number_input("Annual HSA contributions", 0, MAX_HSA, key='spouse_hsa')
                st.number_input("Annual HSA employer match", 0, MAX_HSA, key='spouse_hsa_match')
                if st.session_state['spouse_hsa'] + st.session_state['spouse_hsa_match'] > MAX_HSA:
                    with errors:
                        st.error(f"{st.session_state['spouse_name']}'s HSA contributions exceed allowed maximum")

    with c_after_tax:
        roth_401k_rate = st.slider("Roth 401k Savings Rate", 0, max401k_perc, value=min(max401k_perc, st.session_state.get('roth_401k_rate', 0)), key='roth_401k_rate')
        if ((trad_401k_rate + roth_401k_rate)/100) * salary > MAX_401K:
            with errors:
                st.error("401k contributions exceed allowed maximum")

        primary_magi = get_effective_magi(spouse=False)
        filing_jointly = st.session_state.get('filing_jointly', True) if st.session_state.get('spousal_enabled', False) else True
        combined_magi = get_effective_magi(spouse=True) if st.session_state.get('spousal_enabled', False) and filing_jointly else primary_magi
        primary_roth_max = calculate_roth_ira_max(
            combined_magi,
            st.session_state.get('primary_age', 30),
            filing_jointly
        )
        roth_ira = st.number_input("Annual Roth IRA Contributions", 0, primary_roth_max, key='roth_ira',
                                   help=f"Max based on MAGI: ${primary_roth_max:,}")
        brokerage = st.number_input("After Tax Brokerage Contributions", 0,key='brokerage')
        edu_529 = st.number_input("Annual 529 Savings", 0,value=3_600,key='edu_529')
        st.checkbox("Include 529 in nest egg forecast", key='include_529_in_nest_egg')

        if st.session_state.get('spousal_enabled', False):
            with st.expander(f"{st.session_state.get('spouse_name', 'Spouse2')}'s After-Tax"):
                spouse_sal = st.session_state.get('spouse_salary', 0)
                sp_max401k_perc = int((MAX_401K * 100) / (spouse_sal * 100) * 100) if spouse_sal > 0 else 0
                spouse_roth_rate = st.slider("Roth 401k Savings Rate", 0, max(sp_max401k_perc, 1), key='spouse_roth_401k_rate')
                if ((st.session_state.get('spouse_trad_401k_rate', 0) + spouse_roth_rate) / 100) * spouse_sal > MAX_401K:
                    with errors:
                        st.error(f"{st.session_state['spouse_name']}'s 401k contributions exceed allowed maximum")

                spouse_magi = get_effective_magi(spouse=True)
                spouse_roth_max = calculate_roth_ira_max(
                    combined_magi if filing_jointly else spouse_magi,
                    st.session_state.get('spouse_age', 30),
                    filing_jointly
                )
                st.number_input("Annual Roth IRA Contributions", 0, spouse_roth_max, key='spouse_roth_ira',
                                help=f"Max based on MAGI: ${spouse_roth_max:,}")
                st.number_input("After Tax Brokerage Contributions", 0, key='spouse_brokerage')

    with c_misc:
        children = st.number_input("Number of Children",0,10,value=0,key="children")
        donations = st.number_input("Annual Charitable Donations", 0, value=1_700,key='donations')
        misc_pre_tax_deductions = st.number_input("Pre Tax Payroll Deductions", 0,key='misc_pre_tax_deductions',help="Things like healthcare premiums. This should exclude any retirement contributions handled elsewhere in this tool")
        misc_post_tax_deductions = st.number_input("Post Tax Payroll Deductions", 0,key='misc_post_tax_deductions',help="Things like insurance deductions. This should exclude any retirement contributions handled elsewhere in this tool")
        state_local_income_tax = st.number_input("State and local income tax %",1.,50.0,key='state_local_tax')

        if st.session_state.get('spousal_enabled', False):
            with st.expander(f"{st.session_state.get('spouse_name', 'Spouse2')}'s Deductions"):
                st.number_input("Annual Charitable Donations", 0, key='spouse_donations')
                st.number_input("Pre Tax Payroll Deductions", 0, key='spouse_misc_pre_tax_deductions')
                st.number_input("Post Tax Payroll Deductions", 0, key='spouse_misc_post_tax_deductions')

    with c_down_config:
        try:
            config_dict = {
                'hsa':st.session_state.hsa,
                'hsa_match':st.session_state.hsa_match,
                'roth_ira':st.session_state.roth_ira,
                'trad_401k_rate':st.session_state.trad_401k_rate,
                'roth_401k_rate':st.session_state.roth_401k_rate,
                'salary':st.session_state.salary,
                'bonus': st.session_state.get('bonus', 7.5),
                'min_net_pay':st.session_state.min_net_pay,
                'misc_pre_tax_deductions':st.session_state.misc_pre_tax_deductions,
                'misc_post_tax_deductions':st.session_state.misc_post_tax_deductions,
                'brokerage':st.session_state.brokerage,
                'state_local_tax':st.session_state.state_local_tax,
                'children':st.session_state.children,
                'donations': st.session_state.get('donations', 1700),
                'pay_periods':st.session_state.pay_periods,
                'years_to_retirement':st.session_state.years_to_retirement,
                'roth_ira_start_balance':st.session_state.roth_ira_start_balance,
                'roth_ira_expected_return':st.session_state.roth_ira_expected_return,
                'hsa_start_balance':st.session_state.hsa_start_balance,
                'hsa_expected_return':st.session_state.hsa_expected_return,
                'roth_401k_start_balance':st.session_state.roth_401k_start_balance,
                'roth_401k_expected_return':st.session_state.roth_401k_expected_return,
                'trad_401k_start_balance':st.session_state.trad_401k_start_balance,
                'trad_401k_expected_return':st.session_state.trad_401k_expected_return,
                'edu_529_start_balance':st.session_state.edu_529_start_balance,
                'edu_529_expected_return':st.session_state.edu_529_expected_return,
                'brokerage_start_balance':st.session_state.brokerage_start_balance,
                'brokerage_expected_return': st.session_state.get('brokerage_expected_return', 8),
                'edu_529': st.session_state.get('edu_529', 3600),
                'include_529_in_nest_egg': st.session_state.get('include_529_in_nest_egg', True),
                'spousal_enabled': st.session_state.get('spousal_enabled', False),
                'primary_name': st.session_state.get('primary_name', 'Spouse1'),
                'spouse_name': st.session_state.get('spouse_name', 'Spouse2'),
                'primary_age': st.session_state.get('primary_age', 30),
                'spouse_age': st.session_state.get('spouse_age', 30),
                'filing_jointly': st.session_state.get('filing_jointly', True),
                'spouse_salary': st.session_state.get('spouse_salary', 0),
                'spouse_bonus': st.session_state.get('spouse_bonus', 7.5),
                'spouse_min_net_pay': st.session_state.get('spouse_min_net_pay', 0),
                'spouse_trad_401k_rate': st.session_state.get('spouse_trad_401k_rate', 0),
                'spouse_trad_401k_match_rate': st.session_state.get('spouse_trad_401k_match_rate', 0),
                'spouse_roth_401k_rate': st.session_state.get('spouse_roth_401k_rate', 0),
                'spouse_hsa': st.session_state.get('spouse_hsa', 0),
                'spouse_hsa_match': st.session_state.get('spouse_hsa_match', 0),
                'spouse_roth_ira': st.session_state.get('spouse_roth_ira', 0),
                'spouse_brokerage': st.session_state.get('spouse_brokerage', 0),
                'spouse_misc_pre_tax_deductions': st.session_state.get('spouse_misc_pre_tax_deductions', 0),
                'spouse_misc_post_tax_deductions': st.session_state.get('spouse_misc_post_tax_deductions', 0),
                'spouse_donations': st.session_state.get('spouse_donations', 0),
                'spouse_roth_ira_start_balance': st.session_state.get('spouse_roth_ira_start_balance', 0),
                'spouse_roth_ira_expected_return': st.session_state.get('spouse_roth_ira_expected_return', 8),
                'spouse_hsa_start_balance': st.session_state.get('spouse_hsa_start_balance', 0),
                'spouse_hsa_expected_return': st.session_state.get('spouse_hsa_expected_return', 8),
                'spouse_roth_401k_start_balance': st.session_state.get('spouse_roth_401k_start_balance', 0),
                'spouse_roth_401k_expected_return': st.session_state.get('spouse_roth_401k_expected_return', 8),
                'spouse_trad_401k_start_balance': st.session_state.get('spouse_trad_401k_start_balance', 0),
                'spouse_trad_401k_expected_return': st.session_state.get('spouse_trad_401k_expected_return', 8),
                'spouse_brokerage_start_balance': st.session_state.get('spouse_brokerage_start_balance', 0),
                'spouse_brokerage_expected_return': st.session_state.get('spouse_brokerage_expected_return', 8),
                'spouse_years_to_retirement': st.session_state.get('spouse_years_to_retirement', 25),
            }

            dl_btn = st.download_button("Download Config",icon="💾", data=yaml.dump(config_dict), file_name="401-ok-config.yaml",mime="text/plain",key='config_obj')
            if dl_btn:
                time.sleep(5)
                st.toast("Your config has been saved",icon="💾",duration=10)
        except Exception:
            st.exception("Config could not be downloaded")
