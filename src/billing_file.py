from extract_tsheet import build_cust_df
from metadata import get_pub_hol, get_weekend, get_rates, get_customers
import numpy as np
import pandas as pd

# retrieve public holidays from config file
pub_hol = get_pub_hol()
print(f'Public Holidays: {pub_hol}')

consumer = build_cust_df('consumer')
openserve = build_cust_df('openserve')
hyphen = build_cust_df('hyphen')

print(consumer)


# retrieve rates for custmer from config file
ot_rate = get_rates('consumer')
print(f'OT Rates: {ot_rate}')

# add normal overtime column to dataframe
consumer['Normal_OT'] = np.nan
consumer['High_OT'] = np.nan

print(consumer.info())



def rearrange_hours(cust: str) -> pd.DataFrame:

    #retrieve timesheet for customer
    df = build_cust_df(cust)

    # Parse public holidays (Note: using the key name exactly as given: 'public_hollidays')
    holidays_raw = get_pub_hol()
    holiday_list = [d.strip() for d in holidays_raw.split(',') if d.strip()]
    holidays = set(pd.to_datetime(holiday_list).date) if holiday_list else set()

    # Parse weekend days
    weekend_raw = get_weekend(cust)
    weekend_days = {d.strip() for d in weekend_raw.split(',') if d.strip()}

    # Parse ot_rate dict from the INI (literal JSON-like string)
    ot_rate = get_rates(cust)
    #ot_rate = ast.literal_eval(ot_rate_str) if ot_rate_str.strip() else {}

    # Determine low/high values from the rate dictionary
    # (based on your note that there are two values: e.g., 1.5 (low) and 2 (high))
    unique_rates = sorted(set(ot_rate.values())) if ot_rate else []
    low_rate = unique_rates[0] if unique_rates else 0.0
    high_rate = unique_rates[-1] if unique_rates else 0.0

    # Work on a copy
    #df = consumer.copy()

    # Ensure numeric columns and defaults
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce').fillna(0.0)
    if 'Normal_OT' not in df.columns:
        df['Normal_OT'] = 0.0
    else:
        df['Normal_OT'] = pd.to_numeric(df['Normal_OT'], errors='coerce').fillna(0.0)
    if 'High_OT' not in df.columns:
        df['High_OT'] = 0.0
    else:
        df['High_OT'] = pd.to_numeric(df['High_OT'], errors='coerce').fillna(0.0)

    # Normalize date for comparison
    df['_date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    df['_day'] = df['Day'].astype(str).str.strip()

    def _process_row(row):
        hours = float(row['Hours'])
        day = row['_day']
        date = row['_date']

        # 1) Public holiday
        if date in holidays:
            return pd.Series({'Hours': 0.0, 'Normal_OT': 0.0, 'High_OT': hours})

        # 2) Weekend
        if day in weekend_days:
            day_rate = ot_rate.get(day, low_rate)
            if day_rate == low_rate:
                return pd.Series({'Hours': 0.0, 'Normal_OT': hours, 'High_OT': 0.0})
            else:
                return pd.Series({'Hours': 0.0, 'Normal_OT': 0.0, 'High_OT': hours})

        # 3) Standard overtime if > 8 hours
        if hours > 8.0:
            return pd.Series({'Hours': 8.0, 'Normal_OT': hours - 8.0, 'High_OT': 0.0})

        # 4) Otherwise unchanged
        return pd.Series({'Hours': hours, 'Normal_OT': 0.0, 'High_OT': 0.0})

    df[['Hours', 'Normal_OT', 'High_OT']] = df.apply(_process_row, axis=1)

    # Clean up helper columns
    df.drop(columns=['_date', '_day'], inplace=True)

    return df

# -------------------------
# Example usage (optional):
# -------------------------

customers = get_customers()
for cust in customers:
    consumer = rearrange_hours('consumer')
    print(consumer)