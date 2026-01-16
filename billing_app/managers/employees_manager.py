
import gradio as gr

class EmployeesManager:
    """
    Encapsulates employee management UI and actions (Admin/Employees).
    Simple CRUD wiring; uses mapping states to avoid string splitting.
    """

    # ---------- Helpers ----------
    @staticmethod
    def _build_emp_index(items):
        """
        items: [{'first':..., 'last':...}, ...]
        return:
          labels: ["First Last", ...]
          index:  { "First Last": {"first":..., "last":...}, ... }
        """
        labels, index = [], {}
        for it in (items or []):
            first = (it.get('first') or '').strip()
            last = (it.get('last') or '').strip()
            label = f"{first} {last}".strip()
            labels.append(label)
            index[label] = {"first": first, "last": last}
        return labels, index

    @staticmethod
    def _build_proj_index(items):
        """
        items: [{'client':..., 'project':...}, ...]
        return:
          labels: ["Client - Project", ...]
          index:  { "Client - Project": {"client":..., "project":...}, ... }
        """
        labels, index = [], {}
        for it in (items or []):
            client = (it.get('client') or '').strip()
            proj = (it.get('project') or '').strip()
            label = f"{client} - {proj}".strip()
            labels.append(label)
            index[label] = {"client": client, "project": proj}
        return labels, index

    # ========== Event Handlers ==========
    def e_change_dd_empl(self, value, emp_index):
        """
        Resolve the selected employee from the mapping.
        Returns a dict for e_state: {'fname': first, 'lname': last}
        """
        sel = (emp_index or {}).get(value or "", {})
        return {'fname': sel.get('first'), 'lname': sel.get('last'), 'client': None, 'proj': None}

    def dd_proj_update(self, state):
        """
        Update the project dropdown based on the selected employee in State.
        Returns two outputs:
          1) gr.update(...) for dd_proj
          2) the proj_index mapping state
        """
        from db_helper import get_empl_projects
        first = (state or {}).get('fname')
        last = (state or {}).get('lname')

        if not first or not last:
            return gr.update(choices=[], value=None), {}

        rows = get_empl_projects(first, last) or []  # list of dicts
        labels, index = self._build_proj_index(rows)
        return gr.update(choices=labels, value=(labels[0] if labels else None)), index

    def e_create_btn(self):
        return gr.update(visible=True)

    def e_update_btn(self):
        return gr.update(visible=True)

    def e_delete_btn(self):
        return gr.update(visible=True)

    def click_btn_ok(self, first, last, client, proj, rate, role, emp_index_state):
        """
        Create (insert) an employee record, then refresh the employee dropdown,
        return updated mapping, and hide the create panel.
        """
        from db_helper import employees_insert, get_employee_names
        employees_insert(first, last, client, proj, rate, role)

        # Refresh dropdown choices + mapping
        data = get_employee_names() or []
        labels, index = self._build_emp_index(data)
        selected_val = f"{first} {last}".strip()
        new_val = selected_val if selected_val in labels else (labels[0] if labels else None)

        return (
            gr.update(visible=False),               # pnl_e_create
            gr.update(choices=labels, value=new_val),  # dd_empl
            gr.update(value=""), gr.update(value=""),  # tb_c_first, tb_c_last
            gr.update(value=""), gr.update(value=""),  # tb_c_client, tb_c_proj
            gr.update(value=""), gr.update(value=""),  # tb_c_rate, tb_c_role
            index  # emp_index_state
        )

    def click_btn_update(self, first, last, client, proj, rate, role, emp_index_state):
        """
        Update employee record, then refresh employee dropdown and mapping.
        """
        from db_helper import employees_update, get_employee_names
        employees_update(first, last, client, proj, rate, role)

        data = get_employee_names() or []
        labels, index = self._build_emp_index(data)
        selected_val = f"{first} {last}".strip()
        new_val = selected_val if selected_val in labels else (labels[0] if labels else None)

        return (
            gr.update(visible=False),               # pnl_e_update
            gr.update(choices=labels, value=new_val),  # dd_empl
            index
        )

    def click_btn_delete(self, first, last, emp_index_state):
        """
        Delete employee, then refresh dropdown and mapping.
        """
        from db_helper import employees_delete, get_employee_names
        employees_delete(first, last)

        data = get_employee_names() or []
        labels, index = self._build_emp_index(data)
        new_val = labels[0] if labels else None

        return (
            gr.update(visible=False),               # pnl_e_delete
            gr.update(choices=labels, value=new_val),  # dd_empl
            index
        )

    # ========== UI Builders ==========
    def build_admin_tab(self, parent):
        from db_helper import get_employee_names

        # Initial employee choices + mapping
        data = get_employee_names() or []  # list of dicts
        labels, e_index = self._build_emp_index(data)
        default_emp_value = labels[0] if labels else None

        with parent:
            with gr.Tab("Manage Employees"):
                gr.Markdown("### Manage Employees (Admin)")

                # Mapping states
                e_state = gr.State({'fname': None, 'lname': None, 'client': None, 'proj': None})
                emp_index_state = gr.State(e_index)
                proj_index_state = gr.State({})

                # --- Employee and project selection
                with gr.Row():
                    dd_empl = gr.Dropdown(
                        label="Employee Name",
                        choices=labels,
                        value=default_emp_value,
                        filterable=True
                    )
                    dd_proj = gr.Dropdown(
                        label="Client - Project",
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

                # When employee changes: update state, then refresh project dropdown (and its mapping)
                dd_empl.change(
                    fn=self.e_change_dd_empl,
                    inputs=[dd_empl, emp_index_state],
                    outputs=[e_state]
                ).then(
                    fn=self.dd_proj_update,
                    inputs=[e_state],
                    outputs=[dd_proj, proj_index_state]
                )

                # Show panels
                btn_e_create_empl.click(fn=self.e_create_btn, inputs=[], outputs=[pnl_e_create])
                btn_e_update_empl.click(fn=self.e_update_btn, inputs=[], outputs=[pnl_e_update])
                btn_e_delete_empl.click(fn=self.e_delete_btn, inputs=[], outputs=[pnl_e_delete])

                # --- Create Employee flow
                btn_ok.click(
                    fn=self.click_btn_ok,
                    inputs=[tb_c_first, tb_c_last, tb_c_client, tb_c_proj, tb_c_rate, tb_c_role, emp_index_state],
                    outputs=[pnl_e_create, dd_empl, tb_c_first, tb_c_last, tb_c_client, tb_c_proj, tb_c_rate, tb_c_role, emp_index_state],
                ).then(
                    fn=self.e_change_dd_empl,
                    inputs=[dd_empl, emp_index_state],
                    outputs=[e_state],
                ).then(
                    fn=self.dd_proj_update,
                    inputs=[e_state],
                    outputs=[dd_proj, proj_index_state],
                )

                # --- Update flow
                btn_u_ok.click(
                    fn=self.click_btn_update,
                    inputs=[tb_u_first, tb_u_last, tb_u_client, tb_u_proj, tb_u_rate, tb_u_role, emp_index_state],
                    outputs=[pnl_e_update, dd_empl, emp_index_state],
                ).then(
                    fn=self.e_change_dd_empl,
                    inputs=[dd_empl, emp_index_state],
                    outputs=[e_state],
                ).then(
                    fn=self.dd_proj_update,
                    inputs=[e_state],
                    outputs=[dd_proj, proj_index_state],
                )

                # --- Delete flow
                btn_delete.click(
                    fn=self.click_btn_delete,
                    inputs=[tb_d_first, tb_d_last, emp_index_state],
                    outputs=[pnl_e_delete, dd_empl, emp_index_state],
                ).then(
                    fn=self.e_change_dd_empl,
                    inputs=[dd_empl, emp_index_state],
                    outputs=[e_state],
                ).then(
                    fn=self.dd_proj_update,
                    inputs=[e_state],
                    outputs=[dd_proj, proj_index_state],
                )
'''
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
'''