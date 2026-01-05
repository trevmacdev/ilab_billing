'''
1. Log into application
2. Display tabs based on permissions
    - Admin: Admin, Timesheets, Billing Files
    - User: Timesheets, Billing Files
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
        # Hide login panel, set ROLE
        return gr.update(visible=False), "admin"
    elif usr == "user" and pwd == "user":
        return gr.update(visible=False), "user"

    # Invalid credentials: keep login visible, ROLE stays None
    return gr.update(visible=True), None

####
# END -- EVENT HANDLER FUNCTIONS (FN=)
####

#------------------------------------------------------#

####
# START -- GUI MODULES AND EVENT HANDLERS
####

# 1. Log into application
def build_login(parent, ROLE):
    # Build inside the provided container (Group/Column/etc.)
    with parent:
        gr.Markdown("## Login")
        tb_usr = gr.Textbox(label="Username", placeholder="Enter username")
        tb_pwd = gr.Textbox(label="Password", type="password", placeholder="Enter password")
        btn_login = gr.Button("Login")
        msg = gr.Markdown(visible=False)  # optional message area

    # Wire event: always return two outputs matching [parent, ROLE]
    btn_login.click(
        fn=login_btn,
        inputs=[tb_usr, tb_pwd],
        outputs=[parent, ROLE],  # toggle login panel visibility + set role
    )

    # Return references if you want to use them elsewhere later
    return {
        "tb_usr": tb_usr,
        "tb_pwd": tb_pwd,
        "btn_login": btn_login,
        "msg": msg,
    }

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

        # Login panel (visible by default)
        pnl_login = gr.Group(visible=True)
        build_login(pnl_login, ROLE)

        # NOTE: later you'll add pnl_main = gr.Group(visible=False) and toggle it
        # based on ROLE value in a .then(...) chain after login, or through
        # another callback that reads ROLE.

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
