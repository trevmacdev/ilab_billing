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

# Add a new project
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

def employees_insert(
    f_name,
    l_name,
    proj_client,
    proj_name,
    rate,
    emp_role
):
    cn = get_db_connection()
    cr = cn.cursor()

    cr.callproc(
        'sp_create_employee_insert',
        [f_name, l_name, proj_client, proj_name, rate,emp_role]
    )

    cr.close
    cn.close

    return

####
# END - INSERT STATEMENTS
####
#----------------------------------------------
####
# START - SELECT STATEMENTS
####

# Return proj_client and proj_name from projects
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

# Return app project information from projects
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

# Return employee names from employees
def get_employee_names():
    
    cn = get_db_connection()
    cr = cn.cursor()

    cr.callproc('sp_get_employees_dist')

    e = []  # list of employees in name | surname format.
    for result in cr.stored_results():
        for row in result.fetchall():
            f_name, l_name = row[0], row[1]
            e = f'{f_name} | {l_name}'
            e.append(e)

    cr.close()
    cn.close()

    return e # list of employees in name | surname format.

# return employee projects from employees
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
####
# START - DELETE STATEMENTS
####

# Delete a project from projects
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