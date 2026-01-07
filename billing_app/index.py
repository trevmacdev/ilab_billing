
"""
1. Log into application
2. Display admin tabs for admin profile
3. Enable CRUD of projects into DB
4. Enable CRUD of employees into DB
5. Enable upload and display of selected project timesheeets
6. Enable download of timesheets in pdf format
7. Enable display of billing file information
8. Enable download of billing file in xlsx format.
"""

import gradio as gr
import pandas as pd  # currently unused; keep if you plan to use it later

from metadata import get_gradio_config

#------------------------------------------------------#

#####
# START -- EVENT HANDLER FUNCTIONS (FN=)
#####


# 1. Log into application
def login_btn(usr, pwd):    # Log user in and display dashboard based on role
    # Dummy auth: admin/admin => admin role, user/user => user role
    if usr == "admin" and pwd == "admin":
        # Hide login panel, show admin panel, hide user panel, set ROLE
        return (
            gr.update(visible=False),  # pnl_login
            gr.update(visible=True),   # pnl_admin
            gr.update(visible=False),  # pnl_user
            "admin"                    # ROLE value
        )
    elif usr == "user" and pwd == "user":
        return (
            gr.update(visible=False),  # pnl_login
            gr.update(visible=False),  # pnl_admin
            gr.update(visible=True),   # pnl_user
            "user"                     # ROLE value
        )

    # Invalid credentials: keep login visible, hide both panels, ROLE stays None
    return (
        gr.update(visible=True),   # pnl_login
        gr.update(visible=False),  # pnl_admin
        gr.update(visible=False),  # pnl_user
        None                       # ROLE value
    )


# 3. CRUD Projects

# Create a project
def create_proj_btn():  # Open the create project interface so user can enter project details.
    # Simple toggle
    return (
        gr.update(visible=True),   # pnl_create_proj
        gr.update(visible=False),  # pnl_view_proj_admin
    )


# Insert project details into projects table.
def c_ok_btn(       # Upload a new project to the database.
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
    ot_rate,
    po_start_date,
    po_end_date,
):
    from db_helper import projects_insert, get_client_and_proj

    # insert into db (stored proc or direct)
    projects_insert(    # projects table columns (order matters)
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
        ot_rate,
        po_start_date,
        po_end_date,
    )

    # Refresh dropdown choices from DB and set its selected value to the newly added project
    projects = get_client_and_proj()
    new_key = f"{proj_client} - {proj_name}"

    return (
        # Clear create project fields
        None, None, None, None, None, None, None, None, None, None, None, None, None,
        # Update dropdown choices and select the new project
        gr.update(choices=projects, value=new_key),
        # Assign new project in state
        proj_client, proj_name,
    )


# Read a project
def proj_id_dd(key):    # Display selected project details.
    from db_helper import get_project_info

    # Key expected in the format "PROJ_CLIENT - PROJ_NAME"
    proj_client, proj_name = key.split(" - ", 1)

    # Select * from projects where pk matches key
    proj_info = get_project_info(proj_client, proj_name)

    # Write project info into field values.
    fld_proj_client = f'Client Name: {proj_info["proj_client"]}'
    fld_proj_name = f'Project Name: {proj_info["proj_name"]}'
    fld_job_code = f'Job Code (must match TSheet Job Code #3): {proj_info["job_code"]}'
    fld_ot_rate = f'Overtime Rates: {proj_info["ot_rate"]}'
    fld_weekend = f'Weekend days: {proj_info["weekend"]}'
    fld_client_manager = f'Client Manager: {proj_info["client_manager"]}'
    fld_ilab_manager = f'iLAB Manager: {proj_info["ilab_manager"]}'
    fld_po_number = f'Purchase Order Number: {proj_info["po_number"]}'
    fld_po_start_date = f'PO Start Date: {proj_info["po_start_date"]}'
    fld_po_end_date = f'PO End Date: {proj_info["po_end_date"]}'
    fld_manager_sig = f'Manager Signature Required: {proj_info["manager_sig"]}'
    fld_employee_sig = f'Employee Signature Required: {proj_info["employee_sig"]}'
    fld_notes = f'Timesheet Notes Required: {proj_info["notes"]}'

    return (
        proj_client,  # PROJ_CLIENT
        proj_name,    # PROJ_NAME
        gr.update(visible=True),     # Project info panel

        gr.update(value=fld_proj_client),    # tb_proj_client
        gr.update(value=fld_proj_name),      # tb_proj_name
        gr.update(value=fld_job_code),       # tb_job_code
        gr.update(value=fld_ot_rate),        # tb_ot_rate
        gr.update(value=fld_weekend),        # tb_weekend
        gr.update(value=fld_client_manager), # tb_client_manager
        gr.update(value=fld_ilab_manager),   # tb_ilab_manager
        gr.update(value=fld_po_number),      # tb_po_num
        gr.update(value=fld_po_start_date),  # tb_po_start_date
        gr.update(value=fld_po_end_date),    # tb_po_end_date
        gr.update(value=fld_manager_sig),    # tb_manager_sig
        gr.update(value=fld_employee_sig),   # tb_employee_sig
        gr.update(value=fld_notes),          # tb_notes
    )


# Delete a project
def delete_proj_btn(proj_client, proj_name):    # Delete the selected project from database.
    from db_helper import delete_project
    delete_project(proj_client, proj_name)
    # Reset selected state (simple behavior)
    return None, None  # PROJ_CLIENT and PROJ_NAME


#####
# END -- EVENT HANDLER FUNCTIONS (FN=)
#####


#------------------------------------------------------#

#####
# START -- GUI MODULES AND EVENT HANDLERS
#####


# 1. Log into application
def build_login(parent, pnl_admin, pnl_user, ROLE): # Interface for user login
    # Build inside the provided container (Group/Column/etc.)
    with parent:
        gr.Markdown("## Login")
        tb_usr = gr.Textbox(label="Username", placeholder="Enter username")
        tb_pwd = gr.Textbox(label="Password", type="password", placeholder="Enter password")
        btn_login = gr.Button("Login")
        msg = gr.Markdown(visible=False)  # optional message area

    # Wire event: return four outputs matching [pnl_login, pnl_admin, pnl_user, ROLE]
    btn_login.click(
        fn=login_btn,
        inputs=[tb_usr, tb_pwd],
        outputs=[parent, pnl_admin, pnl_user, ROLE],  # toggle panel visibility + set role
    )

    return {
        "tb_usr": tb_usr,
        "tb_pwd": tb_pwd,
        "btn_login": btn_login,
        "msg": msg,
    }


# 2. Build administrator tabs
def build_admin_tabs(parent, PROJ_CLIENT, PROJ_NAME):   # Interface for administration tabs
    from db_helper import get_client_and_proj

    # Build the tab
    with parent:
        with gr.Tab("Manage Projects"):     # Project management tab
            # Retrieve list of "CLIENT - PROJECT" strings
            projects = get_client_and_proj()

            # Choose a valid default value (either the first project or None)
            default_value = projects[0] if projects and isinstance(projects[0], str) else None

            gr.Markdown("### Manage Projects (Admin)")
            dd_proj_id = gr.Dropdown(       # Dropdown box to select a project
                label="Client - Project",
                choices=projects,
                value=default_value,
                filterable=True
            )

            with gr.Row() as action_row:        # Buttons to create, update and delete a project.
                btn_create_proj = gr.Button("New Project")
                btn_update_proj = gr.Button("Update Project")
                btn_delete_proj = gr.Button("Delete Project")

            # 3. Create new project.
            with gr.Row(visible=False) as pnl_create_proj:  # Interface to enter new project details.
                with gr.Column():   # project info
                    gr.Markdown('Project Info')
                    tb_c_proj_client = gr.Textbox(label='Client Name', interactive=True)
                    tb_c_proj_name = gr.Textbox(label='Project Name', interactive=True)
                    tb_c_job_code = gr.Textbox(label='Job Code (as per TSheet Job Code 3)', interactive=True)
                    tb_c_ot_rate = gr.Textbox(label='Overtime Rates', interactive=True)
                    tb_c_weekend = gr.Textbox(label='Weekend Days', interactive=True)
                with gr.Column():   # personnel and po details
                    gr.Markdown('Personnel and PO details')
                    tb_c_client_manager = gr.Textbox(label='Client Manager', interactive=True)
                    tb_c_ilab_manager = gr.Textbox(label='iLAB Manager', interactive=True)
                    tb_c_po_num = gr.Textbox(label='PO Number', interactive=True)
                    tb_c_po_start_date = gr.Textbox(label='PO Start Date', interactive=True)
                    tb_c_po_end_date = gr.Textbox(label='PO End Date', interactive=True)
                with gr.Column():   # timeshet instructions
                    gr.Markdown('Timesheet instructions')
                    tb_c_manager_sig = gr.Textbox(label='Client Signature Required', interactive=True)
                    tb_c_employee_sig = gr.Textbox(label='Employee Signature Required', interactive=True)
                    tb_c_notes = gr.Textbox(label='Timesheet Notes Required', interactive=True)
                with gr.Column():   # ok and cancel button
                    btn_c_ok = gr.Button('OK')
                    btn_c_cancel = gr.Button('Cancel')

            # 3. Read project details
            with gr.Row(visible=False) as pnl_view_proj_admin:  # View project information
                gr.Markdown('### Project Information')
                with gr.Column():   # project info
                    gr.Markdown('Project Info')
                    tb_proj_client = gr.Textbox(interactive=False)
                    tb_proj_name = gr.Textbox(interactive=False)
                    tb_job_code = gr.Textbox(interactive=False)
                    tb_ot_rate = gr.Textbox(interactive=False)
                    tb_weekend = gr.Textbox(interactive=False)
                with gr.Column():   # personnel and po details
                    gr.Markdown('Personnel and PO details')
                    tb_client_manager = gr.Textbox(interactive=False)
                    tb_ilab_manager = gr.Textbox(interactive=False)
                    tb_po_num = gr.Textbox(interactive=False)
                    tb_po_start_date = gr.Textbox(interactive=False)
                    tb_po_end_date = gr.Textbox(interactive=False)
                with gr.Column():   # timesheet instructions.
                    gr.Markdown('Timesheet instructions')
                    tb_manager_sig = gr.Textbox(interactive=False)
                    tb_employee_sig = gr.Textbox(interactive=False)
                    tb_notes = gr.Textbox(interactive=False)

            # 3. CRUD projects
            # Create projects
            btn_create_proj.click(      # Open interface to create a new project.
                fn=create_proj_btn,
                inputs=[],
                outputs=[
                    pnl_create_proj,      # set visible to true
                    pnl_view_proj_admin,  # set visible to false
                ]
            )

            btn_c_ok.click(     # Submit new project details to database.
                fn=c_ok_btn,
                inputs=[    # pass the components (order matches c_ok_btn signature)
                    tb_c_proj_client,     # proj_client
                    tb_c_proj_name,       # proj_name
                    tb_c_po_num,          # po_num
                    tb_c_client_manager,  # client_manager
                    tb_c_ilab_manager,    # ilab_manager
                    tb_c_job_code,        # job_code
                    tb_c_manager_sig,     # manager_sig
                    tb_c_employee_sig,    # employee_sig
                    tb_c_notes,           # notes
                    tb_c_weekend,         # weekend
                    tb_c_ot_rate,         # ot_rate
                    tb_c_po_start_date,   # po_start_date
                    tb_c_po_end_date,     # po_end_date
                ],
                outputs=[   # blank tb_c_* fields, update dropdown, set project state variables.
                    # blank out field values
                    tb_c_proj_client,
                    tb_c_proj_name,
                    tb_c_job_code,
                    tb_c_ot_rate,
                    tb_c_weekend,
                    tb_c_client_manager,
                    tb_c_ilab_manager,
                    tb_c_po_num,
                    tb_c_po_start_date,
                    tb_c_po_end_date,
                    tb_c_manager_sig,
                    tb_c_employee_sig,
                    tb_c_notes,
                    # update dropdown choices and selected value
                    dd_proj_id,
                    # select project in state variables
                    PROJ_CLIENT,
                    PROJ_NAME,
                ],
            )

            # Read projects
            dd_proj_id.change(          # A new project has been selected or is available.
                fn=proj_id_dd,
                inputs=[dd_proj_id],    # pass the component, gradio provides selected value
                outputs=[
                    PROJ_CLIENT,    # set state value
                    PROJ_NAME,      # set state value
                    pnl_view_proj_admin, # set visible true
                    # project field values / content
                    tb_proj_client,
                    tb_proj_name,
                    tb_job_code,
                    tb_ot_rate,
                    tb_weekend,
                    tb_client_manager,
                    tb_ilab_manager,
                    tb_po_num,
                    tb_po_start_date,
                    tb_po_end_date,
                    tb_manager_sig,
                    tb_employee_sig,
                    tb_notes,
                ]
            )

            btn_delete_proj.click(      # delete
                fn=delete_proj_btn,
                inputs=[
                    PROJ_CLIENT,
                    PROJ_NAME,
                ],
                outputs=[
                    PROJ_CLIENT,
                    PROJ_NAME,
                ]
            )

        with gr.Tab("Manage Employees"):    # Employee management tab
            gr.Markdown("### Manage Employees (Admin)")
            emp_name = gr.Textbox(label="Employee Name")
            emp_role = gr.Dropdown(
                label="Role",
                choices=["Developer", "Tester", "Project Manager", "Analyst"],
            )
            btn_add_emp = gr.Button("Add Employee")
            emp_out = gr.Textbox(label="Result", interactive=False)
            btn_add_emp.click(
                lambda n, r: f"[ADMIN] Employee added: {n} - {r}",
                inputs=[emp_name, emp_role],
                outputs=[emp_out],
            )

    return


# 3. Build user tabs
def build_user_tabs(parent):    # Interface for user tabs
    with parent:
        with gr.Tab("Manage Projects"):
            gr.Markdown("### Manage Projects (User)")
            proj_name = gr.Textbox(label="Project Name")
            proj_code = gr.Textbox(label="Project Code")
            btn_add_proj = gr.Button("Add Project")
            proj_out = gr.Textbox(label="Result", interactive=False)
            btn_add_proj.click(
                lambda n, c: f"[USER] Project added: {n} ({c})",
                inputs=[proj_name, proj_code],
                outputs=[proj_out],
            )

        with gr.Tab("Manage Employees"):
            gr.Markdown("### Manage Employees (User)")
            emp_name = gr.Textbox(label="Employee Name")
            emp_role = gr.Dropdown(
                label="Role",
                choices=["Developer", "Tester", "Project Manager", "Analyst"],
            )
            btn_add_emp = gr.Button("Add Employee")
            emp_out = gr.Textbox(label="Result", interactive=False)
            btn_add_emp.click(
                lambda n, r: f"[USER] Employee added: {n} - {r}",
                inputs=[emp_name, emp_role],
                outputs=[emp_out],
            )
    return


#####
# END -- GUI MODULES AND EVENT HANDLERS
#####


#------------------------------------------------------#

#####
# START -- GUI CONTROL BLOCK (CALL GUI MODULES)
#####


def build_app():
    with gr.Blocks(title="Billing App") as billing_app:
        # STATE VARIABLES
        ROLE = gr.State(value=None)  # 1. Log into application - can be admin or user

        PROJ_CLIENT = gr.State(value=None) # Currently selected proj_client in projects table
        PROJ_NAME = gr.State(value=None)   # Currently selected proj_name in projects table

        # Page header
        gr.Markdown("# iLAB Billing App")

        # Define panels
        pnl_login = gr.Column(visible=True)       # Login panel (visible by default)
        pnl_admin = gr.Tabs(visible=False)        # Administrator panel
        pnl_user = gr.Tabs(visible=False)         # User panel

        # Build panels
        build_login(pnl_login, pnl_admin, pnl_user, ROLE)
        build_admin_tabs(pnl_admin, PROJ_CLIENT, PROJ_NAME)
        build_user_tabs(pnl_user)

    return billing_app


#####
# END -- GUI CONTROL BLOCK (CALL GUI MODULES)
#####


#------------------------------------------------------#

#####
#   START SERVER
#####


gradio_config = get_gradio_config()

if __name__ == "__main__":
    build_app().launch(
        server_name=gradio_config.get("server_name", None),
        server_port=gradio_config.get("server_port", None),
        show_error=gradio_config.get("show_error", True),
        share=gradio_config.get("share", False),
        show_api=gradio_config.get("show_api", False),
        allowed_paths=gradio_config.get("allowed_paths", None),
    )
