
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
def login_btn(usr, pwd):
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
def create_proj_btn():
    # Placeholder: implement your "create" logic and return updated state if needed
    return (
        gr.update(visible=True), # pnl_create_proj
        gr.update(visible=False), # pnl_view_proj_admin
        # gr.update(visible=False), # pnl_update_proj
    )

# Insert project details into projects table.
def c_ok_btn():

    # call stored proc to insert into db

    # set project state variables to the new project
    # clear pnl_create_proj fields and add pnl_create_proj to view project dropdown.
    return

# Read a project
def proj_id_dd(key):
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
def delete_proj_btn(proj_client, proj_name):
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
def build_login(parent, pnl_admin, pnl_user, ROLE):
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

    # Return references if you want to use them elsewhere later
    return {
        "tb_usr": tb_usr,
        "tb_pwd": tb_pwd,
        "btn_login": btn_login,
        "msg": msg,
    }

# 2. Build administrator tabs
def build_admin_tabs(parent, PROJ_CLIENT, PROJ_NAME):
    from db_helper import get_client_and_proj

    # Build the tab
    with parent:
        with gr.Tab("Manage Projects"):
            # Retrieve list of "CLIENT - PROJECT" strings
            projects = get_client_and_proj()

            # Choose a valid default value (either the first project or None)
            default_value = projects[0] if projects and isinstance(projects[0], str) else None

            gr.Markdown("### Manage Projects (Admin)")
            dd_proj_id = gr.Dropdown(
                label="Client - Project",
                choices=projects,
                value=default_value,
                filterable=True
            )

            with gr.Row() as action_row:
                btn_create_proj = gr.Button("New Project")
                btn_update_proj = gr.Button("Update Project")
                btn_delete_proj = gr.Button("Delete Project")

            # 3. Create new project.
            with gr.Row(visible=False) as pnl_create_proj:
                with gr.Column():
                    gr.Markdown('Project Info')
                    tb_c_proj_client = gr.Textbox(label='Client Name', interactive=True)
                    tb_c_proj_name = gr.Textbox(label='Project Name', interactive=True)
                    tb_c_job_code = gr.Textbox(label='Job Code (as per TSheet Job Code 3)', interactive=True)
                    tb_c_ot_rate = gr.Textbox(label='Overtime Rates', interactive=True)
                    tb_c_weekend = gr.Textbox(label='Weekend Days', interactive=True)
                with gr.Column():
                    gr.Markdown('Personnel and PO details')
                    tb_c_client_manager = gr.Textbox(label='Client Manager', interactive=True)
                    tb_c_ilab_manager = gr.Textbox(label='iLAB Manager', interactive=True)
                    tb_c_po_num = gr.Textbox(label='PO Number', interactive=True)
                    tb_c_po_period = gr.Textbox(label='PO Period', interactive=True)
                with gr.Column():
                    gr.Markdown('Timesheet instructions')
                    tb_c_manager_sig = gr.Textbox(label='Client Signature Required', interactive=True)
                    tb_c_employee_sig = gr.Textbox(label='Employee Signature Required', interactive=True)
                    tb_c_notes = gr.Textbox(label='Timesheet Notes Required', interactive=True)
                with gr.Column():
                    btn_c_ok = gr.Button('OK')
                    btn_c_cancel = gr.Button('Cancel')

            # 3. Read project details
            with gr.Row(visible=False) as pnl_view_proj_admin:
                gr.Markdown('### Project Information')
                with gr.Column():
                    gr.Markdown('Project Info')
                    tb_proj_client = gr.Textbox(interactive=False)
                    tb_proj_name = gr.Textbox(interactive=False)
                    tb_job_code = gr.Textbox(interactive=False)
                    tb_ot_rate = gr.Textbox(interactive=False)
                    tb_weekend = gr.Textbox(interactive=False)
                with gr.Column():
                    gr.Markdown('Personnel and PO details')
                    tb_client_manager = gr.Textbox(interactive=False)
                    tb_ilab_manager = gr.Textbox(interactive=False)
                    tb_po_num = gr.Textbox(interactive=False)
                    tb_po_start_date = gr.Textbox(interactive=False)
                    tb_po_end_date = gr.Textbox(interactive=False)
                with gr.Column():
                    gr.Markdown('Timesheet instructions')
                    tb_manager_sig = gr.Textbox(interactive=False)
                    tb_employee_sig = gr.Textbox(interactive=False)
                    tb_notes = gr.Textbox(interactive=False)

            

            # 3. CRUD projects
            # Create projects
            btn_create_proj.click(      # create
                fn=create_proj_btn,
                inputs=[],
                outputs=[
                    pnl_create_proj, # set visible to true
                    pnl_view_proj_admin, # set visible to false
                    # pnl_update_proj,    # set visible to false    -- not created yet
                ]
            )

            btn_c_ok.click(
                fn=c_ok_btn,
                inputs=[],
                outputs=[],
            )
            
            # TODO: btn_c_cancel.click needs to clear the pnl_create_proj fields, hide pnl_create_proj and show pnl_view_proj_admin

            # Read projects
            dd_proj_id.change(          # read
                fn=proj_id_dd,
                inputs=[dd_proj_id],    # pass the component, not its .value
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

        with gr.Tab("Manage Employees"):
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
def build_user_tabs(parent):
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
