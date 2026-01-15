import gradio as gr


class EmployeesManager:
    """
    Encapsulates employee management UI and actions (Admin/Employees).
    Simple CRUD wiring; assumes db_helper functions commit changes.
    """

    # ========== Event Handlers ==========

    def e_change_dd_empl(self, value):
        """
        When employee changes, store the selected employee in State.
        Expects 'value' in 'First | Last' format.
        Returns a dict for e_state: {'fname': first, 'lname': last}
        """
        if not value or "|" not in value:
            return {'fname': None, 'lname': None, 'client': None, 'proj': None}

        first, last = [s.strip() for s in value.split("|", 1)]
        return {'fname': first, 'lname': last, 'client': None, 'proj': None}

    def dd_proj_update(self, state):
        """
        Update the project dropdown based on the selected employee in State.
        State format: {'fname': ..., 'lname': ...}
        Returns a single gr.update(...) for the dd_proj component.
        """
        from db_helper import get_empl_projects

        first = (state or {}).get('fname')
        last = (state or {}).get('lname')

        if not first or not last:
            return gr.update(choices=[], value=None)

        # get_empl_projects should return list of strings like: "First | Last | Client | Project"
        rows = get_empl_projects(first, last) or []

        proj_choices = []
        for r in rows:
            parts = [p.strip() for p in r.split("|")]
            # parts: [First, Last, Client, Project]
            if len(parts) >= 4:
                proj_choices.append(f"{parts[2]} | {parts[3]}")

        return gr.update(
            choices=proj_choices,
            value=(proj_choices[0] if proj_choices else None)
        )

    def e_create_btn(self):
        return gr.update(visible=True)

    def e_update_btn(self):
        return gr.update(visible=True)

    def e_delete_btn(self):
        return gr.update(visible=True)

    def click_btn_ok(self, first, last, client, proj, rate, role):
        """
        Create (insert) an employee record, then refresh the employee dropdown and hide the panel.
        """
        from db_helper import employees_insert, get_employee_names

        employees_insert(first, last, client, proj, rate, role)

        # Refresh dropdown choices
        choices = get_employee_names() or []
        selected_val = f"{first} | {last}"
        new_val = selected_val if selected_val in choices else (choices[0] if choices else None)

        # Hide panel + update employee dropdown + clear the create fields
        return (
            gr.update(visible=False),  # pnl_e_create
            gr.update(choices=choices, value=new_val),  # dd_empl
            gr.update(value=""), gr.update(value=""),  # tb_c_first, tb_c_last
            gr.update(value=""), gr.update(value=""),  # tb_c_client, tb_c_proj
            gr.update(value=""), gr.update(value=""),  # tb_c_rate, tb_c_role
        )

    def click_btn_update(self, first, last, client, proj, rate, role):
        """
        Update employee record, then refresh employee dropdown and hide update panel.
        """
        from db_helper import employees_update, get_employee_names

        employees_update(first, last, client, proj, rate, role)
        choices = get_employee_names() or []
        selected_val = f"{first} | {last}"
        new_val = selected_val if selected_val in choices else (choices[0] if choices else None)

        return (
            gr.update(visible=False),  # pnl_e_update
            gr.update(choices=choices, value=new_val)  # dd_empl
        )

    def click_btn_delete(self, first, last):
        """
        Delete employee, then refresh dropdown and hide delete panel.
        """
        from db_helper import employees_delete, get_employee_names

        employees_delete(first, last)
        choices = get_employee_names() or []
        new_val = choices[0] if choices else None

        return (
            gr.update(visible=False),  # pnl_e_delete
            gr.update(choices=choices, value=new_val)  # dd_empl
        )

    # ========== UI Builders ==========

    def build_admin_tab(self, parent):
        from db_helper import get_employee_names

        # State keeps currently selected employee & aux fields
        e_state = gr.State({'fname': None, 'lname': None, 'client': None, 'proj': None})

        c = get_employee_names() or []
        default_emp_value = c[0] if c else None

        with parent:
            with gr.Tab("Manage Employees"):
                gr.Markdown("### Manage Employees (Admin)")

                # --- Employee and project selection
                with gr.Row():
                    dd_empl = gr.Dropdown(
                        label="Employee Name",
                        choices=c,
                        value=default_emp_value,
                        filterable=True
                    )

                    dd_proj = gr.Dropdown(
                        label="Client | Project",
                        choices=[],
                        value=None,
                        filterable=True
                    )

                gr.Markdown("The client, project and employee information is treated as one entity.")
                gr.Markdown("The project must exist before the employee can be created (see Manage Projects tab).")

                # --- Action buttons
                with gr.Row():
                    btn_e_create_empl = gr.Button("Add Employee")
                    btn_e_update_empl = gr.Button("Update Employee")
                    btn_e_delete_empl = gr.Button("Delete Employee")

                # --- Create panel
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
                            tb_c_role = gr.Textbox(label="Role")
                        btn_ok = gr.Button("OK")

                # --- Update panel
                with gr.Row(visible=False) as pnl_e_update:
                    with gr.Column():
                        gr.Markdown("Update Employee")
                        with gr.Row():
                            tb_u_first = gr.Textbox(label="First Name")
                            tb_u_last = gr.Textbox(label="Last Name")
                        with gr.Row():
                            tb_u_client = gr.Textbox(label="Client")
                            tb_u_proj = gr.Textbox(label="Project")
                        with gr.Row():
                            tb_u_rate = gr.Textbox(label="Rate")
                            tb_u_role = gr.Textbox(label="Role")
                        btn_u_ok = gr.Button("Save")

                # --- Delete panel
                with gr.Row(visible=False) as pnl_e_delete:
                    with gr.Column():
                        gr.Markdown("Delete Employee")
                        with gr.Row():
                            tb_d_first = gr.Textbox(label="First Name")
                            tb_d_last = gr.Textbox(label="Last Name")
                        btn_delete = gr.Button("Confirm Delete")

                # --- Wiring events

                # When employee changes: update state, then refresh project dropdown
                dd_empl.change(
                    fn=self.e_change_dd_empl,
                    inputs=[dd_empl],
                    outputs=[e_state]
                ).then(
                    fn=self.dd_proj_update,
                    inputs=[e_state],
                    outputs=[dd_proj]
                )

                # Show panels
                btn_e_create_empl.click(fn=self.e_create_btn, inputs=[], outputs=[pnl_e_create])
                btn_e_update_empl.click(fn=self.e_update_btn, inputs=[], outputs=[pnl_e_update])
                btn_e_delete_empl.click(fn=self.e_delete_btn, inputs=[], outputs=[pnl_e_delete])

                # --- Create Employee flow
                # 1) Insert -> hide panel and update dd_empl
                # 2) Then set state from new dd_empl
                # 3) Then refresh dd_proj based on the (new) selected employee
                btn_ok.click(
                    fn=self.click_btn_ok,
                    inputs=[tb_c_first, tb_c_last, tb_c_client, tb_c_proj, tb_c_rate, tb_c_role],
                    outputs=[pnl_e_create, dd_empl, tb_c_first, tb_c_last, tb_c_client, tb_c_proj, tb_c_rate,
                             tb_c_role],
                ).then(
                    fn=self.e_change_dd_empl,
                    inputs=[dd_empl],
                    outputs=[e_state],
                ).then(
                    fn=self.dd_proj_update,
                    inputs=[e_state],
                    outputs=[dd_proj],
                )

                # --- Update flow
                btn_u_ok.click(
                    fn=self.click_btn_update,
                    inputs=[tb_u_first, tb_u_last, tb_u_client, tb_u_proj, tb_u_rate, tb_u_role],
                    outputs=[pnl_e_update, dd_empl],
                ).then(
                    fn=self.e_change_dd_empl,
                    inputs=[dd_empl],
                    outputs=[e_state],
                ).then(
                    fn=self.dd_proj_update,
                    inputs=[e_state],
                    outputs=[dd_proj],
                )

                # --- Delete flow
                btn_delete.click(
                    fn=self.click_btn_delete,
                    inputs=[tb_d_first, tb_d_last],
                    outputs=[pnl_e_delete, dd_empl],
                ).then(
                    fn=self.e_change_dd_empl,
                    inputs=[dd_empl],
                    outputs=[e_state],
                ).then(
                    fn=self.dd_proj_update,
                    inputs=[e_state],
                    outputs=[dd_proj],
                )

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
