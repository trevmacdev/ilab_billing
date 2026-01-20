import pandas as pd
from billing_app.db_helper import get_proj_id, get_job_code, get_ot_rate

#===== HELPER METHODS - All called from TSFormatter.process_tsheet
def create_dataframe(csv_path):
    return pd.read_csv(csv_path)

def remove_cols(df):
    return df[[
        'fname',
        'lname',
        'local_date',
        'local_day',
        'hours',
        'jobcode_3',
        'notes'
    ]]


def clean_data_issues(df):
    df = df.replace('Hyphen” for Hyphen', 'Hyphen for Hyphen', regex=False)
    return df

def rename_cols(df):
    return df.rename(columns={
        'fname': 'First Name',
        'lname': 'Last Name',
        'local_date': 'Date',
        'local_day': 'Day',
        'hours': 'Hours',
        'jobcode_3': 'Job Code',
        'notes': 'Notes'
    })

# Update the timesheet dataframe with overtime
def ot_calc(df, id):
    # Step 1: Retrieve overtime rates from the projects table.
    ot_rates = get_ot_rate(id)
    print(f'ot_rates: {ot_rates}')

    return df

#===== MAIN FORMATTING CLASS - Prepares workable timesheet dataframes.
class TSFormatter:
    @staticmethod
    def process_csv(csv):
        # convert raw csv file to a dataframe
        df = create_dataframe(csv)

        # reduce df to needed columns only
        df = remove_cols(df)

        # clean known metadata issues
        df = clean_data_issues(df)

        # rename columns
        df = rename_cols(df)

        return df

    @staticmethod
    def built_cust_df(proj_client: str, proj_name: str, df: pd.DataFrame):

        # get the project id
        id = get_proj_id(proj_client, proj_name)    # db_helper
        print(f'id = {id}')

        # get job code for client | project pair from projects
        jc = get_job_code(id)   # db_helper
        print(f'jc = {jc}')

        # build a dataframe using the job code (jc)
        df = df[df['Job Code'] == jc]
        print(f'df with job code {df}')

        df = ot_calc(df, id)

        return df


#===== MODULE TEST ONLY ====

tsf = TSFormatter()
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent
CSV_NAME = 'timesheet.csv'
CSV_PATH = SCRIPT_DIR / CSV_NAME

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

df = tsf.process_csv(CSV_PATH)
print(f"process_csv: {df['Job Code']}")

df = tsf.built_cust_df('Telkom', 'Consumer', df)
print(f'build_cust_df: {df}')

