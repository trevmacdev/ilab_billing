###########
# UTILITY MODILE TO HANDLE METADATA IN CONFIG.PROPERTIES FILE
# SHOULD BE EASY ENOUGH TO MODIFY TO PULL FROM A DATABASE LATER
# THE CALLABLES SIMPLY RETURN THE REQUESTED VALUES SO THIS IS THE ONLY PLACE WHERE METADATA CHANGES WILL NEED TO BE MADE
###########

import configparser as cp
import json
from pathlib import Path
# from pub_holidays import pub_hol
from datetime import date


###########
# START -- PATH AND CONFIG HANDLING
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
# END -- PATH AND CONFIG HANDLING
###########

###########
# START -- GET WEB SERVER CONFIG
###########

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

###########
# END -- GET WEB SERVER CONFIG
###########

def get_mysql_config():

    DB_HOST = config.get('database', 'host')
    DB_PORT = config.get('database', 'port')
    DB_USER = config.get('database', 'user')
    DB_PWD = config.get('database', 'pwd')
    DB_SCHEMA = config.get('database', 'schema')

    cn = {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PWD,
        'database': DB_SCHEMA
    }

    return cn

###########
# START -- GET DB INFO
###########


###########
# END -- GET DB INFO
###########



