MAX_401K = 24_500
MAX_ROTH_IRA = 7_500
ROTH_IRA_CATCHUP = 1_100
MAX_HSA = 8_750

ROTH_IRA_PHASE_OUT_SINGLE = (153_000, 168_000)
ROTH_IRA_PHASE_OUT_JOINT = (242_000, 252_000)

STANDARD_DEDUCTION = 32_200
STANDARD_DEDUCTION_SINGLE = 16_100
CHILD_TAX_CREDIT = 2_200

BRACKETS_SINGLE = [
    (12_400, 0.10),
    (50_400, 0.12),
    (105_700, 0.22),
    (201_775, 0.24),
    (256_225, 0.32),
    (640_600, 0.35),
]

BRACKETS_JOINT = [
    (24_800, 0.10),
    (100_800, 0.12),
    (211_400, 0.22),
    (403_550, 0.24),
    (512_450, 0.32),
    (768_700, 0.35),
]

ACCOUNT_KEYS = [
    'roth_401k',
    'trad_401k',
    'hsa',
    'edu_529',
    'brokerage',
    'roth_ira'
]

BRACKETS = BRACKETS_JOINT

SPOUSE_ACCOUNT_KEYS = [
    'roth_ira',
    'hsa',
    'roth_401k',
    'trad_401k',
    'brokerage'
]
