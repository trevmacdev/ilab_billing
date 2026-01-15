
from metadata import get_mysql_config
import mysql.connector

# Establish a db connection
def get_db_connection():
    details = get_mysql_config()
    cn = mysql.connector.connect(
        host=details['host'],
        user=details['user'],
        password=details['password'],
        database=details['database'],
        port=details['port'],
        autocommit=True
    )
    return cn

# ======================
# INSERT / UPDATE / DELETE
# ======================

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
        cur.callproc(
            'sp_create_project_insert',
            [
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
    try:
        cr = cn.cursor()
        cr.callproc(
            'sp_create_employee_insert',
            [f_name, l_name, proj_client, proj_name, rate, emp_role]
        )
    finally:
        cr.close()
        cn.close()

def employees_update(
    f_name,
    l_name,
    proj_client,
    proj_name,
    rate,
    emp_role
):
    cn = get_db_connection()
    try:
        cr = cn.cursor()
        # Assumes stored procedure exists with this signature
        cr.callproc(
            'sp_update_employee',
            [f_name, l_name, proj_client, proj_name, rate, emp_role]
        )
    finally:
        cr.close()
        cn.close()

def employees_delete(f_name, l_name):
    cn = get_db_connection()
    try:
        cr = cn.cursor()
        # Assumes stored procedure exists with this signature
        cr.callproc('sp_delete_employee', [f_name, l_name])
    finally:
        cr.close()
        cn.close()

def delete_project(proj_client, proj_name):
    cn = get_db_connection()
    try:
        cr = cn.cursor()
        cr.callproc('sp_delete_project', [proj_client, proj_name])
    finally:
        cr.close()
        cn.close()

# ======================
# SELECTS (structured results)
# ======================

# Return [{'proj_client': ..., 'proj_name': ...}, ...]
def get_client_and_proj():
    cn = get_db_connection()
    try:
        cr = cn.cursor()
        cr.callproc("sp_get_projects_clients")
        out = []
        for result in cr.stored_results():
            for row in result.fetchall():
                proj_client, proj_name = row[0], row[1]
                out.append({
                    "proj_client": (proj_client or "").strip(),
                    "proj_name": (proj_name or "").strip()
                })
        return out
    finally:
        cr.close()
        cn.close()

# Return a single dict of project info (column names -> values)
def get_project_info(proj_client, proj_name):
    cn = get_db_connection()
    try:
        cr = cn.cursor(dictionary=True)
        cr.callproc('sp_get_project_details', [proj_client, proj_name])
        result_row = None
        for result in cr.stored_results():
            rows = result.fetchall()
            if rows:
                result_row = rows[0]
                break
        return result_row
    finally:
        cr.close()
        cn.close()

# Return [{'first': ..., 'last': ...}, ...]
def get_employee_names():
    cn = get_db_connection()
    try:
        cr = cn.cursor()
        cr.callproc('sp_get_employees_dist')
        out = []
        for result in cr.stored_results():
            for row in result.fetchall():
                first = (row[0] or '').strip()
                last = (row[1] or '').strip()
                out.append({"first": first, "last": last})
        return out
    finally:
        cr.close()
        cn.close()

# Return [{'client': ..., 'project': ...}, ...] for a given employee
def get_empl_projects(f_name, l_name):
    cn = get_db_connection()
    try:
        cr = cn.cursor()
        cr.callproc('sp_get_empl_projects', [f_name, l_name])
        out = []
        for result in cr.stored_results():
            for row in result.fetchall():
                client, proj = row[0], row[1]
                out.append({
                    "client": (client or '').strip(),
                    "project": (proj or '').strip()
                })
        return out
    finally:
        cr.close()
        cn.close()
