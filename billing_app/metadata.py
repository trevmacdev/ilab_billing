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