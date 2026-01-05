###########
# UTILITY MODILE TO HANDLE METADATA IN CONFIG.PROPERTIES FILE
# SHOULD BE EASY ENOUGH TO MODIFY TO PULL FROM A DATABASE LATER
# THE CALLABLES SIMPLY RETURN THE REQUESTED VALUES SO THIS IS THE ONLY PLACE WHERE METADATA CHANGES WILL NEED TO BE MADE
###########

import configparser as cp
import json
from pathlib import Path
from pub_holidays import pub_hol
from datetime import date

###########
# PATH AND CONFIG HANDLING
###########

# Set project path
SCRIPT_DIR = Path(__file__).resolve().parent

# Load config file
CONFIG_PATH = SCRIPT_DIR / "config.properties"

# Load the configuration file.
config = cp.ConfigParser()
config.read(CONFIG_PATH)

# Set file paths
TSHEET_PATH = SCRIPT_DIR / config.get('paths', 'timesheet')

###########
# RETRIEVE CONFIG VALUES
###########

# extract customers from config
def get_customers():
    # example data: "consumer, openserve, hyphen"
    customers = config.get('global', 'customer')
    return [c.strip() for c in customers.split(',') if c.strip()]

# extract manager from config
def get_manager(cust: str):
    # example data: "Joe Soap"
    return config.get(f'customer.{cust}', 'manager')

# extract employees from config
def get_employees(cust: str):
    # example data: "Luthando Adams, Another Employee"
    return config.get(f'customer.{cust}', 'employees')

# extract employee rates from config - same order as employees
def get_rates(cust:str):
    return config.get(f'customer.{cust}', 'rates')

# extract job code from confg
def get_jobcode(cust: str):
    # example data: "Consumer" - Matches the jobcode_3 field in timesheet.csv
    return config.get(f'customer.{cust}', 'jobcode')

# extract manager sig
def get_manager_sig(cust: str):
    # example data: "True"
    return config.get(f'customer.{cust}', 'manager_sig')

# extract employee sig
def get_employee_sig(cust: str):
    # example data: "True"
    return config.get(f'customer.{cust}', 'employee_sig')

def get_notes(cust: str):
    # example data: "True"
    return config.get(f'customer.{cust}', 'notes')

def get_rates(cust: str):
    # example data: '{"Mon": 1.5, "Tue": 1.5, "Wed": 1.5, "Thu": 1.5, "Fri": 1.5, "Sat": 1.5, "Sun": 2, "Pub": 2}' - Dictionary
    return json.loads(config[f'customer.{cust}'] ['ot_rate'])
                        
def get_pub_hol():
    # example data: 2025-01-01,2025-03-21,2025-04-18
    
    # Stores 3 years of public holidays, to ensure coverage for year-end timesheets
    # Check when public holidays were last updated

    ph = config.get('global', 'public_holidays')
    last_year = str(date.today().year - 1)
    curr_year = str(date.today().year)
    conf_year = {d[:4] for d in ph}
    if last_year not in conf_year:
        # Fetch new public holidays and update config file
        ph = pub_hol(curr_year)
        config.set('global', 'public_holidays', ph)
        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
    
    # return public holidays
    return ph

def get_weekend(cust):
    return config.get(f'customer.{cust}', 'weekend')

def get_billing_path(cust):
    # append a folder for the current month and year to the billing file folder.
    full_path = config.get(f'customer.{cust}', 'file_path') / str(date.today().month) + str(date.today().year)
    return full_path

def get_po(cust):
    return config.get(f'customer.{cust}', 'po_num')

def get_gradio_config():
    server_name = config.get('gradio', 'server_name')
    server_port = config.getint('gradio', 'server_port')
    show_error = config.getboolean('gradio', 'show_error')
    share = config.getboolean('gradio', 'share')
    show_api = config.getboolean('gradio', 'show_api')
    allowed_paths = [
        SCRIPT_DIR / config.get('paths', 'pdf'),
        SCRIPT_DIR / config.get('paths', 'xls')
    ]
    grad = {
        'server_name': server_name,
        'server_port': server_port,
        'show_error': show_error,
        'share': share,
        'show_api': show_api,
        'allowed_paths': allowed_paths
    }
    return grad

