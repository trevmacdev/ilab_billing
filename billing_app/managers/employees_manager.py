
import gradio as gr

class EmployeesManager:
    """
    Encapsulates employee management UI and actions (Admin/User).
    Currently provides simple placeholders for CRUD; wire to DB when ready.
    """

    def e_create_btn(self):
        return gr.update(visible=True)

    def e_update_btn(self):
        return gr.update(visible=True)

    def e_delete_btn(self):
        return gr.update(visible=True)

    def build_admin_tab(self, parent):
        from db_helper import get_employees, get_empl_projects

        with parent:
            with gr.Tab("Manage Employees"):
                empl = get_employees()

                gr.Markdown("### Manage Employees (Admin)")
                dd_client_proj_empl = gr.Dropdown(
                    label='Client - Project - Employee',
                    choices=empl_proj if empl_proj else None,
                    value=empl_proj[0] if (empl_proj and isinstance(empl_proj[0], str)) else None,
                    filterable=True
                )
                
                gr.Markdown('The client, project and employee information is treated as one entity.')
                gr.Markdown('The project must exist before the employee can be created (see Manage Projects tab).')

                with gr.Row():
                    btn_e_create_empl = gr.Button('Add Employee')
                    btn_e_update_empl = gr.Button('Update Employee')
                    btn_e_delete_empl = gr.Button('Delete Employee')

                with gr.Row(visible=False) as pnl_e_create:
                    with gr.Column():
                        gr.Markdown("Create Employee")
                        tb_e_first = gr.Textbox(label="First Name")
                        tb_e_last = gr.Textbox(label="Last Name")
                        tb_e_client = gr.Textbox(label="Client")
                        tb_e_proj = gr.Textbox(label="Project")
                        btn_e_create_ok = gr.Button("OK")

                with gr.Row(visible=False) as pnl_e_update:
                    with gr.Column():
                        gr.Markdown("Update Employee (placeholder)")
                        tb_eu_first = gr.Textbox(label="First Name")
                        tb_eu_last = gr.Textbox(label="Last Name")
                        tb_eu_client = gr.Textbox(label="Client")
                        tb_eu_proj = gr.Textbox(label="Project")
                        btn_e_update_ok = gr.Button("Save")

                with gr.Row(visible=False) as pnl_e_delete:
                    with gr.Column():
                        gr.Markdown("Delete Employee (placeholder)")
                        btn_e_delete_ok = gr.Button("Confirm Delete")

                btn_e_create_empl.click(fn=self.e_create_btn, inputs=[], outputs=[pnl_e_create])
                btn_e_update_empl.click(fn=self.e_update_btn, inputs=[], outputs=[pnl_e_update])
                btn_e_delete_empl.click(fn=self.e_delete_btn, inputs=[], outputs=[pnl_e_delete])

                # TODO: Wire btn_e_create_ok / btn_e_update_ok / btn_e_delete_ok to db_helper

    def build_user_tab(self, parent):
        with parent:
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
