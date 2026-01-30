import pandas as pd

from billing_app.db_helper import get_proj_id, get_job_code, get_ot_rate, get_weekend
from billing_app.metadata import get_pub_hollidays


# ===== HELPER METHODS - All called from TSFormatter.process_tsheet

def create_dataframe(csv_path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def remove_cols(df: pd.DataFrame) -> pd.DataFrame:
    return df[[
        'fname',
        'lname',
        'local_date',
        'local_day',
        'hours',
        'jobcode_3',
        'notes'
    ]]


def clean_data_issues(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace('Hyphen” for Hyphen', 'Hyphen for Hyphen', regex=False)
    return df


def rename_cols(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={
        'fname': 'First Name',
        'lname': 'Last Name',
        'local_date': 'Date',
        'local_day': 'Day',
        'hours': 'Normal Hrs',
        'jobcode_3': 'Job Code',
        'notes': 'Notes'
    })


# Update the timesheet dataframe with overtime
def ot_calc(df: pd.DataFrame, proj_id: int) -> pd.DataFrame:
    import ast  # convert strings to dicts

    # Step 1: Retrieve overtime rates from the projects table.
    ot_rates = ast.literal_eval(get_ot_rate(proj_id))
    #print(f'ot_rates: {ot_rates}')

    # Get unique overtime values to create additional df columns
    unique_rates = sorted(set(ot_rates.values()))
    #print(f'Unique overtime rates: {unique_rates}')

    insert_at = df.columns.get_loc('Normal Hrs') + 1  # index after Normal Hrs

    # Create a dict that contains the 'ot rate value': 'column name' for easy insertion later
    rate_cols = {}

    # Insert OT columns and build mapping rate -> column name
    for i, v in enumerate(unique_rates):
        col_name = f'{v} x Hrs'
        df.insert(insert_at + i, col_name, 0)
        rate_cols[str(v)] = col_name

    #print(f'rate_cols: {rate_cols}')

    # Load weekend/public holiday values
    weekend = get_weekend(proj_id)
    we = [d.strip() for d in weekend.split(',') if d.strip()]
    #print(f'we: {we}')

    ph = get_pub_hollidays()
    #print(f'public holidays: {ph}')


    # Loop through each row in df.
    for index, row in df.iterrows():
        normal_hours = float(row['Normal Hrs'])

        # 1) Public holiday: move full hours into Pub rate column
        if str(row['Date']) in ph:
            ot_r = ot_rates['Pub']
            ot_col = rate_cols[str(ot_r)]
            df.at[index, 'Normal Hrs'] = 0
            df.at[index, ot_col] = normal_hours
            continue

        # 2) Weekend: move full hours into that day's OT rate column
        if row['Day'] in we:
            ot_r = ot_rates[row['Day']]
            ot_col = rate_cols[str(ot_r)]
            df.at[index, 'Normal Hrs'] = 0
            df.at[index, ot_col] = normal_hours
            continue

        # 3) Weekday overtime: > 8 hours => 8 normal, balance to OT rate column
        if normal_hours > 8:
            ot_r = ot_rates[row['Day']]
            ot_col = rate_cols[str(ot_r)]
            df.at[index, 'Normal Hrs'] = 8
            df.at[index, ot_col] = normal_hours - 8

    #print(f'Overtime Hours inserted into df:\n{df}')
    return df


# ===== MAIN FORMATTING CLASS - Prepares workable timesheet dataframes.
class TSFormatter:
    @staticmethod
    def process_csv(csv) -> pd.DataFrame:
        df: pd.DataFrame = create_dataframe(csv)
        df = remove_cols(df)
        df = clean_data_issues(df)
        df = rename_cols(df)
        return df

    @staticmethod
    def built_cust_df(proj_client: str, proj_name: str, df: pd.DataFrame) -> pd.DataFrame:
        proj_id = get_proj_id(proj_client, proj_name)
        #print(f'proj_id = {proj_id}')

        jc = get_job_code(proj_id)
        #print(f'jc = {jc}')

        df = df[df['Job Code'] == jc]
        #print(f'df with job code:\n{df}')

        df = ot_calc(df, proj_id)
        return df


# ===== MODULE TEST ONLY ====

if __name__ == "__main__":
    from pathlib import Path

    tsf = TSFormatter()

    SCRIPT_DIR = Path(__file__).parent
    CSV_NAME = 'timesheet.csv'
    CSV_PATH = SCRIPT_DIR / CSV_NAME

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    df = tsf.process_csv(CSV_PATH)
    #print(f"process_csv Job Code column:\n{df['Job Code']}")

    df = tsf.built_cust_df('Telkom', 'Consumer', df)
    #print(f'build_cust_df result:\n{df}')