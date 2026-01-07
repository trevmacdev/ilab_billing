from metadata import get_mysql_config
import mysql.connector
import json

# Establish a db connection
def get_db_connection():

    details = get_mysql_config()

    try:
        cn = mysql.connector.connect(
            host = details['host'],
            user = details['user'],
            password = details['password'],
            database = details['database'],
            port = details['port'],
            autocommit = True
        )

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    return cn



####
# START - INSERT STATEMENTS
####

# The project table contains a list of projects per client and purchase order. Billing is generally caried out per purchase order
def projects_insert(
    proj_client,
    proj_name,
    po_num,
    client_manager,
    ilab_manager,
    job_code,
    manager_sig,
    employee_sig,
    notes,
    weekend,
    rate,
    po_start_date,
    po_end_date
):
    cn = get_db_connection()

    try:
        cur = cn.cursor()
        
        # Call stored proc
        cur.callproc('sp_create_project_insert',[
            proj_client,
            proj_name,
            po_num,
            client_manager,
            ilab_manager,
            job_code,
            manager_sig,
            employee_sig,
            notes,
            weekend,
            rate,
            po_start_date,
            po_end_date
            ]
        )
        
    finally:
        cur.close()
        cn.close()


####
# END - INSERT STATEMENTS
####

#----------------------------------------------

####
# START - SELECT STATEMENTS
####

# Return client and project name
def get_client_and_proj():
    
    cn = get_db_connection()

    cr = cn.cursor()
    cr.callproc("sp_get_projects_clients")

    choices = []
    for result in cr.stored_results():
        for row in result.fetchall():
            proj_client, proj_name = row[0], row[1]
            display = f'{proj_client} - {proj_name}'
            choices.append(display)
    
    cr.close()
    cn.close()
    
    return choices

# Return project information
def get_project_info(proj_client, proj_name):

    cn = get_db_connection()

    cr = cn.cursor(dictionary=True)
    cr.callproc('sp_get_project_details', [proj_client, proj_name])

    project_info = None
    for result in cr.stored_results():
        rows = result.fetchall()     # We only expect one record
        if rows:
            result_row = rows[0]
        break

    
    cr.close()
    cn.close()

    return result_row

def get_employees():
    
    cn = get_db_connection()
    cr = cn.cursor()

    cr.callproc('sp_get_employees_dist')

    choices = []
    for result in cr.stored_results():
        for row in result.fetchall():
            f_name, l_name = row[0], row[1]
            display = f'{f_name} | {l_name}'
            choices.append(display)

    cr.close()
    cn.close()

    return choices

def get_empl_projects(f_name, l_name):
    cn = get_db_connection()
    cr = cn.cursor()

    cr.callproc('sp_get_empl_projects', [f_name, l_name])

    choices = []
    for result in cr.stored_results():
        for row in result.fetchall():
            client, proj = row[0], row[1]
            display = f'{f_name} | {l_name} | {client} | {proj}'
            choices.append(display)

    cr.close()
    cn.close()

    return choices

####
# END - SELECT STATEMENTS
####

#----------------------------------------------

# sp_delete_project

####
# START - DELETE STATEMENTS
####

def delete_project(proj_client, proj_name):

    cn = get_db_connection()
    cr = cn.cursor()

    cr.callproc('sp_delete_project', [proj_client, proj_name])

    cr.close()
    cn.close()
    return

####
# END - DELETE STATEMENTS
####