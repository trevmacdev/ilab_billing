
import gradio as gr

class ProjectsManager:
    """
    Encapsulates all project CRUD functions and UI (Admin/User).
    """

    # --- Event Handler Functions (Admin) ---

    def create_proj_btn(self):
        return (gr.update(visible=True), gr.update(visible=False))

    def c_ok_btn(
        self,
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

        projects_insert(
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

        projects = get_client_and_proj()
        new_key = f"{proj_client} - {proj_name}"

        return (
            None, None, None, None, None, None, None, None, None, None, None, None, None,
            gr.update(choices=projects, value=new_key),
            proj_client, proj_name,
        )

    def proj_id_dd(self, key):
        from db_helper import get_project_info

        print('Triggered proj_id_dd on dropbox change')
        proj_client, proj_name = key.split(" - ", 1)
        proj_info = get_project_info(proj_client, proj_name)

        fld_proj_client = f'Client Name: {proj_info["proj_client"]}'
        fld_proj_name = f'Project Name: {proj_info["proj_name"]}'
        fld_job_code = f'Job Code (must match TSheet Job Code #3): {proj_info["job_code"]}'
        fld_ot_rate = f'Overtime Rates: {proj_info["ot_rate"]}'
        fld_weekend = f'Weekend days: {proj_info["weekend"]}'
        fld_client_manager = f'Client Manager: {proj_info["client_manager"]}'
        fld_ilab_manager = f'iLAB Manager: {proj_info["ilab_manager"]}'
        fld_po_number = f'Purchase Order Number: {proj_info["po_num"]}'
        fld_po_start_date = f'PO Start Date: {proj_info["po_start_date"]}'
        fld_po_end_date = f'PO End Date: {proj_info["po_end_date"]}'
        fld_manager_sig = f'Manager Signature Required: {proj_info["manager_sig"]}'
        fld_employee_sig = f'Employee Signature Required: {proj_info["employee_sig"]}'
        fld_notes = f'Timesheet Notes Required: {proj_info["notes"]}'

        return (
            proj_client,
            proj_name,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value=fld_proj_client),
            gr.update(value=fld_proj_name),
            gr.update(value=fld_job_code),
            gr.update(value=fld_ot_rate),
            gr.update(value=fld_weekend),
            gr.update(value=fld_client_manager),
            gr.update(value=fld_ilab_manager),
            gr.update(value=fld_po_number),
            gr.update(value=fld_po_start_date),
            gr.update(value=fld_po_end_date),
            gr.update(value=fld_manager_sig),
            gr.update(value=fld_employee_sig),
            gr.update(value=fld_notes),
        )

    def delete_proj_btn(self, proj_client, proj_name):
        from db_helper import delete_project, get_client_and_proj
        delete_project(proj_client, proj_name)
        choices = get_client_and_proj()
        return (
            None, None,
            gr.update(choices=choices),
            gr.update(value=choices[0] if choices else None),
        )

    # --- UI Builders ---

    def build_admin_tab(self, parent, PROJ_CLIENT, PROJ_NAME):
        from db_helper import get_client_and_proj

        with parent:
            with gr.Tab("Manage Projects"):
                projects = get_client_and_proj()
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
                        tb_c_po_start_date = gr.Textbox(label='PO Start Date', interactive=True)
                        tb_c_po_end_date = gr.Textbox(label='PO End Date', interactive=True)
                    with gr.Column():
                        gr.Markdown('Timesheet instructions')
                        tb_c_manager_sig = gr.Textbox(label='Client Signature Required', interactive=True)
                        tb_c_employee_sig = gr.Textbox(label='Employee Signature Required', interactive=True)
                        tb_c_notes = gr.Textbox(label='Timesheet Notes Required', interactive=True)
                    with gr.Column():
                        btn_c_ok = gr.Button('OK')
                        btn_c_cancel = gr.Button('Cancel')

                with gr.Row(visible=False) as pnl_view_proj_admin:
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

                # Wiring

                btn_create_proj.click(
                    fn=self.create_proj_btn,
                    inputs=[],
                    outputs=[pnl_create_proj, pnl_view_proj_admin]
                )

                btn_c_ok.click(
                    fn=self.c_ok_btn,
                    inputs=[
                        tb_c_proj_client,
                        tb_c_proj_name,
                        tb_c_po_num,
                        tb_c_client_manager,
                        tb_c_ilab_manager,
                        tb_c_job_code,
                        tb_c_manager_sig,
                        tb_c_employee_sig,
                        tb_c_notes,
                        tb_c_weekend,
                        tb_c_ot_rate,
                        tb_c_po_start_date,
                        tb_c_po_end_date,
                    ],
                    outputs=[
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
                        dd_proj_id,
                        PROJ_CLIENT,
                        PROJ_NAME,
                    ],
                )

                dd_proj_id.change(
                    fn=self.proj_id_dd,
                    inputs=[dd_proj_id],
                    outputs=[
                        PROJ_CLIENT,
                        PROJ_NAME,
                        pnl_view_proj_admin,
                        pnl_create_proj,
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

                btn_delete_proj.click(
                    fn=self.delete_proj_btn,
                    inputs=[PROJ_CLIENT, PROJ_NAME],
                    outputs=[PROJ_CLIENT, PROJ_NAME, dd_proj_id, dd_proj_id]
                )

    def build_user_tab(self, parent):
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
