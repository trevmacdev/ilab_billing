
from billing_app.metadata import get_mysql_config
import mysql.connector

# =========================================
# DB CONNECTION
# =========================================

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


# =========================================
# GENERIC HELPERS
# =========================================

def exec_proc(sp, params=None):
    """
    Call a stored procedure that does not need rows back (INSERT/UPDATE/DELETE).
    """
    if params is None:
        params = []
    cn = get_db_connection()
    try:
        cr = cn.cursor()
        cr.callproc(sp, params)
    finally:
        cr.close()
        cn.close()


def get_one_row(sp, params=None):
    """
    Returns a single row (as a dict), or None.
    Assumes the first result set is the one we want.
    """
    if params is None:
        params = []
    cn = get_db_connection()
    try:
        cr = cn.cursor(dictionary=True)
        cr.callproc(sp, params)

        row = None
        for result in cr.stored_results():
            rec = result.fetchone()
            if rec is not None:
                row = rec
            break  # only consider the first result set

        return row
    finally:
        cr.close()
        cn.close()


def get_many_rows(sp, params=None):
    """
    Returns a list of rows (each as a dict). Empty list if no rows.
    Assumes the first result set is the one we want.
    """
    if params is None:
        params = []
    cn = get_db_connection()
    try:
        cr = cn.cursor(dictionary=True)
        cr.callproc(sp, params)

        rows = []
        for result in cr.stored_results():
            rows = result.fetchall()
            break  # only consider the first result set

        return rows
    finally:
        cr.close()
        cn.close()


def first_value(row):
    """
    Given a dict row, return the first column's value.
    Returns None if row is None/empty.
    Useful for procs that select a single column.
    """
    if not row:
        return None
    # row is a dict because our helpers use dictionary=True
    for v in row.values():
        return v
    return None


# =========================================
# INSERT / UPDATE / DELETE
# =========================================

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
    exec_proc(
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


def employees_insert(
    f_name,
    l_name,
    proj_client,
    proj_name,
    rate,
    emp_role
):
    exec_proc(
        'sp_create_employee_insert',
        [f_name, l_name, proj_client, proj_name, rate, emp_role]
    )


def employees_update(
    f_name,
    l_name,
    proj_client,
    proj_name,
    rate,
    emp_role
):
    exec_proc(
        'sp_update_employee',
        [f_name, l_name, proj_client, proj_name, rate, emp_role]
    )


def employees_delete(f_name, l_name):
    exec_proc('sp_delete_employee', [f_name, l_name])


def delete_project(proj_client, proj_name):
    exec_proc('sp_delete_project', [proj_client, proj_name])


# =========================================
# SELECTS (structured results)
# =========================================

# Return [{'proj_client': ..., 'proj_name': ...}, ...]
def get_client_and_proj():
    """
    Expects the proc to return columns like:
    - proj_client
    - proj_name

    We normalize the keys and strip whitespace.
    """
    rows = get_many_rows('sp_get_projects_clients', [])
    out = []
    for r in rows:
        proj_client = (r.get('proj_client', '') or '').strip()
        proj_name = (r.get('proj_name', '') or '').strip()
        out.append({
            'proj_client': proj_client,
            'proj_name': proj_name
        })
    return out


# Return a single dict of project info (column names -> values)
def get_project_info(proj_client, proj_name):
    """
    Returns a dict of project details, or None if not found.
    """
    return get_one_row('sp_get_project_details', [proj_client, proj_name])


# Return [{'first': ..., 'last': ...}, ...]
def get_employee_names():
    """
    Expects the proc to return columns like:
    - f_name
    - l_name
    We map them to 'first' and 'last'.
    """
    rows = get_many_rows('sp_get_employees_dist', [])
    out = []
    for r in rows:
        first = (r.get('f_name', '') or '').strip()
        last = (r.get('l_name', '') or '').strip()
        out.append({'first': first, 'last': last})
    return out


# Return [{'client': ..., 'project': ...}, ...] for a given employee
def get_empl_projects(f_name, l_name):
    """
    Expects the proc to return columns like:
    - proj_client
    - proj_name
    We map them to 'client' and 'project'.
    """
    rows = get_many_rows('sp_get_empl_projects', [f_name, l_name])
    out = []
    for r in rows:
        client = (r.get('proj_client', '') or '').strip()
        project = (r.get('proj_name', '') or '').strip()
        out.append({'client': client, 'project': project})
    return out


def get_job_code(id):
    """
    Returns a single scalar (first column), or None.
    """
    row = get_one_row('sp_get_proj_jobcode', [id])
    return first_value(row)


def get_proj_id(proj_client, proj_name):
    """
    Returns a single scalar (first column), or None.
    """
    row = get_one_row('sp_get_proj_id', [proj_client, proj_name])
    return first_value(row)


def get_ot_rate(id):
    """
    Returns a single scalar (first column), or None.
    """
    row = get_one_row('sp_get_proj_ot_rate', [id])
    return first_value(row)

def get_weekend(id):
    row = get_one_row('sp_get_proj_weekend', [id])
    return first_value(row)
