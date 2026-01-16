import gradio as gr

class TimesheetTabs:

    # ========== Event Handlers ==========

    # ========== UI Builders ==========
    def build_ts_tab(self, parent):

        with parent:
            with gr.Tab('Timesheets'):
                with gr.Row():
                    with gr.Column(scale=1, min_width=220): # left column contains file upload, buttons and tsheet selection radio buttons
                        file = gr.File(
                            file_types=['.csv'],
                            type='filepath',
                            label='Upload Raw TSheet (csv)'
                        )
                        chkbx_timesheet = gr.CheckboxGroup(
                            choices=None,    # extract client - project from db if it exists in the job code exists in the tsheet job_code_3
                            info='Select customers for billing',
                            type='value',
                            interactive='True',
                            visible='False',
                            container='True'
                        )
                        with gr.Group('ts_buttons', visible=False):
                            btn_t_ok = gr.Button('OK')
                            with gr.Row():
                                btn_t_back = gr.Button('<-', interactive=False)
                                btn_t_next = gr.Button('->', interactive=False)
                    with gr.Column(scale=5):
                        ts_view = gr.DataFrame(wrap=True)

