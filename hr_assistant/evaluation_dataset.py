""" Evaluation_dataset — the hand-written question / reference-answer
pairs the evaluation scores against.

Reference answers are taken straight from data/*.txt — keep them in sync if
the corpus changes. This is data, not logic, so it lives on its own.
"""

DATASET_NAME = "hr-policy-qa"

TEST_CASES = [
    {"question": "How many days of paid annual leave do I get per year?",
     "answer": "18 days of paid annual leave per calendar year, accrued at 1.5 days per completed month of service."},
    {"question": "How many days of unused annual leave can be carried forward?",
     "answer": "Up to 10 days; any balance beyond that is forfeited on December 31st."},
    {"question": "How many paid sick days do I get per year?",
     "answer": "10 days of paid sick leave per calendar year; it does not carry forward."},
    {"question": "How many days per week can I work from home?",
     "answer": "Up to 2 days per week as a standing arrangement, agreed with your manager."},
    {"question": "How long is the probation period?",
     "answer": "3 months (90 calendar days) from the date of joining, unless the offer letter says otherwise."},
    {"question": "What is the notice period during probation?",
     "answer": "15 days' written notice, or payment in lieu of notice."},
    {"question": "What is the standard notice period for a confirmed employee?",
     "answer": "60 days (2 calendar months); 90 days for Director level and above."},
    {"question": "Within how many days must reimbursement claims be submitted?",
     "answer": "Within 30 days of the expense being incurred."},
    {"question": "How many public holidays does the company observe each year?",
     "answer": "12 fixed public holidays per calendar year, plus 2 floating holidays."},
    {"question": "How much is the one-time home office setup allowance?",
     "answer": "Up to 15,000 (local currency), claimable within the first 3 months of WFH eligibility."},
]