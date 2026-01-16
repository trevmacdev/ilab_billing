
import gradio as gr
from metadata import get_gradio_config

# Local modules
from auth.login import build_login
from managers.projects_manager import ProjectsManager
from managers.employees_manager import EmployeesManager
from billing.ts_tabs import TimesheetTabs

def build_app():
    proj_mgr = ProjectsManager()
    emp_mgr = EmployeesManager()
    ts_tabs = TimesheetTabs()

    with gr.Blocks(title="Billing App") as billing_app:
        # STATE VARIABLES
        ROLE = gr.State(value=None)  # can be "admin" or "user"
        EMPL = gr.State({'fname': None, 'l_name': None, 'client': None, 'proj': None})

        PROJ_CLIENT = gr.State(value=None) # selected proj_client in projects table
        PROJ_NAME = gr.State(value=None)   # selected proj_name in projects table

        # Page header
        gr.Markdown("# iLAB Billing App")

        # Panels
        pnl_login = gr.Column(visible=True)       # Login panel
        pnl_admin = gr.Tabs(visible=False)        # Admin panel
        pnl_ts_tabs = gr.Tabs(visible=False)         # User panel

        # Build panels
        build_login(pnl_login, pnl_admin, pnl_ts_tabs, ROLE)

        # Admin tabs (split across classes)
        proj_mgr.build_admin_tab(pnl_admin, PROJ_CLIENT, PROJ_NAME)
        emp_mgr.build_admin_tab(pnl_admin)

        # Timesheet tabs
        ts_tabs.build_ts_tab(pnl_ts_tabs)

    return billing_app

# --- START SERVER ---
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
