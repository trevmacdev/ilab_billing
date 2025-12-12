import pandas as pd
from metadata import get_jobcode, get_notes

from timesheet_pdf import build_cust_pdf

def clean_raw(raw_ts):
    # Pass in raw_tsheet from billing_app.py as raw_ts

    # reduce raw_ts to needed columns
    raw_ts = raw_ts[[
        'fname',
        'lname',
        'local_date',
        'local_day',
        'hours',
        'jobcode_3',
        'notes'
    ]]

    # clean up known data value issues
    raw_ts = raw_ts.replace('Hyphen” for Hyphen', 'Hyphen for Hyphen', regex=False)

    # rename columns
    raw_ts = raw_ts.rename(columns={
        'fname': 'First Name',
        'lname': 'Last Name',
        'local_date': 'Date',
        'local_day': 'Day',
        'hours': 'Hours',
        'jobcode_3': 'Cust',
        'notes': 'Notes'
    })

    return raw_ts

# build customer dataframe
def build_cust_df(cust: str, raw_ts):
    # Pass in customer name and raw_tsheet from billing_app.py

    ts = raw_ts[raw_ts['Cust'] == get_jobcode(cust)]
    if get_notes(cust) == False:
        ts = ts.drop('Notes', axis=1)
    return ts

'''
consumer = build_cust_df('consumer')
openserve = build_cust_df('openserve')
hyphen = build_cust_df('hyphen')



build_cust_pdf('consumer', consumer)
build_cust_pdf('openserve', openserve)
build_cust_pdf('hyphen', hyphen)
'''