from openpyxl import Workbook, load_workbook
from pathlib import Path
from extract_tsheet import build_cust_df
from metadata import get_pub_hol, get_weekend, get_rates, get_customers, get_company, get_po, get_po_period,        get_employees, get_ot, get_roles
import numpy as np
import pandas as pd

def overtime(cust, df):
# retrieve public holidays from config file
    pub_hol = get_pub_hol()
    print(f'Public Holidays: {pub_hol}')

    # retrieve rates for custmer from config file
    ot_rate = get_ot(cust)
    print(f'OT Rates: {ot_rate}')

    # add normal overtime column to dataframe
    df['Normal_OT'] = np.nan
    df['High_OT'] = np.nan

    print(df.info())



def rearrange_hours(cust: str, df: pd.DataFrame) -> pd.DataFrame:

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

def create_billing_df(cust, df):

    # Prep dataframe
    # Drop the Cust and Notes column, we don't need it here.
    df = df.drop(columns=['Cust', 'Notes'])
    
    # Calculate overtime hours
    df = rearrange_hours(cust, df)

    print('Display final dataframe')
    print(df)

    return df

def create_billing_excel(cust, df):

    # -- Get all metadata for billing file
    company = get_company(cust)
    po_num = get_po(cust)
    po_period = get_po_period(cust)
    resources = get_employees(cust)
    rates = get_rates(cust)
    ot_multiplier = get_ot(cust)
    empl_roles = get_roles(cust)
     
    # --- Get timesheet dates to append to filename. 
    # Convert to datetime (keeps it simple; adjust format if needed)
    dates = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')

    first_date = dates.min().strftime('%Y-%m-%d')
    last_date  = dates.max().strftime('%Y-%m-%d')
    date_range = f"{first_date}_to_{last_date}"

    # Set save path and filename
    # --- Paths ---
    SCRIPT_DIR = Path(__file__).resolve().parent
    XLS_FN = f"billing_files/{company}-billing-{date_range}.xlsx"
    XLS_PATH = SCRIPT_DIR / XLS_FN

    try:
        # Try open the workbook if it exists.
        wb = load_workbook(XLS_PATH)
        print(f'Opened existing excel file: {XLS_FN}')
    except FileNotFoundError:
        # If file doesn't exist, create a new one.
        wb = Workbook()
        print(f'Created new excel file: {XLS_FN}')

    # Create Summary worksheet if it doesn't exist.
    if 'Summary'not in wb.worksheets:
        ws = wb['Summary']


    wb.save(XLS_PATH)
    return (
        XLS_PATH,
        XLS_FN
    )

def process_billing(cust, df):

    # Create a billing file dataframe for cust
    df = create_billing_df(cust, df)

    pth, fn = create_billing_excel(cust, df)

    return(

    )

