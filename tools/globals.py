MAX_401K = 24_500
MAX_ROTH_IRA = 7_500
MAX_HSA = 8_750
STANDARD_DEDUCTION = 32_200
CHILD_TAX_CREDIT = 2_200 

BRACKETS = [ 
    ( 24_800, 0.10), 
    (100_800, 0.12), 
    (211_400, 0.22),
    (403_550, 0.24),
    (512_450, 0.32)
]

ACCOUNT_KEYS = [
    'roth_401k',
    'trad_401k',
    'hsa',
    'edu_529',
    'brokerage',
    'roth_ira'
]
DEFAULTS = { 
    'hsa':0,
    'hsa_match': 0,
    'roth_ira': 0,
    'trad_401k_rate': 15,
    'trad_401k_match_rate': 3,
    'roth_401k_rate': 0,
    'edu_529': 0,
    'salary':60_000,
    'min_net_pay': 3_500,
    'misc_pre_tax_deductions':1_000,
    'misc_post_tax_deductions':1_000,
    'brokerage':0,
    'state_local_tax':5.0,
    'taxable_income':0,
    'children':0,
    'years_to_retirement':25,
    'roth_ira_start_balance':0,
    'roth_ira_expected_return':8,
    'hsa_start_balance':0,
    'hsa_expected_return':8,
    'roth_401k_start_balance':0,
    'roth_401k_expected_return':8,
    'trad_401k_start_balance':0,
    'trad_401k_expected_return':8,
    'edu_529_start_balance':0,
    'edu_529_expected_return':8,
    'brokerage_start_balance':0,
    'brokerage_expected_return':8,
}
