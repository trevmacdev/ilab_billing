
'''
1. Log into application
2. Display admin tabs for admin profile
3. Enable CRUD of projects into DB
4. Enable CRUD of employees into DB
5. Enable upload and display of selected project timesheeets
6. Enable download of timesheets in pdf format
7. Enable display of billing file information
8. Enable download of billing file in xlsx format.
'''

import gradio as gr
import pandas as pd  # currently unused; keep if you plan to use it later

from metadata import get_gradio_config

#------------------------------------------------------#

####
# START -- EVENT HANDLER FUNCTIONS (FN=)
####

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

####
# END -- EVENT HANDLER FUNCTIONS (FN=)
####

#------------------------------------------------------#

####
# START -- GUI MODULES AND EVENT HANDLERS
####

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

# 2. Administrator Tabs
    # Tab creation handled at deisgn

# 3. CRUD Projects

# Create a project
def create_proj_btn():
    return


# 2. Build administrator tabs
def build_admin_tabs(parent):
    from db_helper import get_client_and_proj
    
    # Get client and project into to populate proj_id
    choices = get_client_and_proj()
    with parent:
        with gr.Tab("Manage Projects"):
            gr.Markdown("### Manage Projects (Admin)")
            proj_id = gr.Dropdown(
                label="Client - Project",
                choices=choices,
                filterable=True)

            with gr.Row():
                btn_create_proj = gr.Button("New Project")
                btn_read_proj = gr.Button("View Project")
                btn_update_proj = gr.Button("Update Project")
                btn_delete_proj = gr.Button("Delete Project")

            btn_create_proj.click(
                fn=create_proj_btn,
                inputs=[],
                outputs=[]
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

####
# END -- GUI MODULES AND EVENT HANDLERS
####

#------------------------------------------------------#

####
# START -- GUI CONTROL BLOCK (CALL GUI MODULES)
####

def build_app():
    with gr.Blocks(title="Billing App") as billing_app:
        # STATE VARIABLES
        ROLE = gr.State(value=None)  # 1. Log into application - can be admin or user

        # Page header
        gr.Markdown("# iLAB Billing App")

        # Define panels
        pnl_login = gr.Column(visible=True)       # Login panel (visible by default)
        pnl_admin = gr.Tabs(visible=False)        # Administrator panel
        pnl_user = gr.Tabs(visible=False)         # User panel

        # Build panels
        build_login(pnl_login, pnl_admin, pnl_user, ROLE)
        build_admin_tabs(pnl_admin)
        build_user_tabs(pnl_user)

    return billing_app

####
# END -- GUI CONTROL BLOCK (CALL GUI MODULES)
####

#------------------------------------------------------#

####
#   START SERVER
####

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
