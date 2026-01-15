
import gradio as gr

class EmployeesManager:
    """
    Encapsulates employee management UI and actions (Admin/Employees).
    Currently provides simple placeholders for CRUD; wire to DB when ready.
    """

    def e_create_btn(self):
        return gr.update(visible=True)

    def e_update_btn(self):
        return gr.update(visible=True)

    def e_delete_btn(self):
        return gr.update(visible=True)

    def build_admin_tab(self, parent):
        from db_helper import get_employee_names

        with parent:
            with gr.Tab("Manage Employees"):
                empl = get_employee_names()
                
                gr.Markdown("### Manage Employees (Admin)")

                with gr.Row():  # Employee and project selection.

                    dd_empl = gr.Dropdown(  # Select employee name
                        label = 'Employee Name',
                        choices = empl,
                        value = None,
                        filterable=True
                    )

                    dd_proj = gr.Dropdown(      # Select project
                        # Populate on dd_empl.change.
                        label='Client - Project - Employee',
                        choices = None,
                        value =  None,
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
                        with gr.Row():
                            tb_c_first = gr.Textbox(label="First Name")
                            tb_c_last = gr.Textbox(label="Last Name")
                        with gr.Row():
                            tb_c_client = gr.Textbox(label="Client")
                            tb_c_proj = gr.Textbox(label="Project")
                        with gr.Row():
                            tb_c_rate = gr.Textbox(label="Rate")
                            tb_c_row = gr.Textbox(label="Row")
                        btn__ok = gr.Button("OK")

                with gr.Row(visible=False) as pnl_e_update:
                    with gr.Column():
                        gr.Markdown("Update Employee (placeholder)")
                        with gr.Row():
                            tb_u_first = gr.Textbox(label="First Name")
                            tb_u_last = gr.Textbox(label="Last Name")
                        with gr.Row():
                            tb_u_client = gr.Textbox(label="Client")
                            tb_u_proj = gr.Textbox(label="Project")
                        with gr.Row():
                            tb_u_rate = gr.Textbox(label="Rate")
                            tb_u_row = gr.Textbox(label="Row")
                        btn_save = gr.Button("Save")

                with gr.Row(visible=False) as pnl_e_delete:
                    with gr.Column():
                        gr.Markdown("Delete Employee (placeholder)")
                        btn_delete = gr.Button("Confirm Delete")

                btn_e_create_empl.click(fn=self.e_create_btn, inputs=[], outputs=[pnl_e_create])
                btn_e_update_empl.click(fn=self.e_update_btn, inputs=[], outputs=[pnl_e_update])
                btn_e_delete_empl.click(fn=self.e_delete_btn, inputs=[], outputs=[pnl_e_delete])

                # TODO: Wire btn_ok / btn_save / btn_delete

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
