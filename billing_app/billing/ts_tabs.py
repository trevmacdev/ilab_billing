import gradio as gr
import pandas as pd
from billing_app.formatter.ts_build import TSFormatter

class TimesheetTabs:

    tsf = TSFormatter() # Format timesheet dataframes.

    # ========== Event Functions ==========

    # ========== UI Builders ==========
    def build_ts_tab(self, parent):
        with parent:
            gr.Markdown('### Upload your full Tsheet csv file. Make sure the dates on the file match your billing dates.')
            with gr.Tab('Timesheets'):

                # Declare state variables
                cur_df = gr.State(pd.DataFrame())   # Dataframe assigned to ts_view (gr.DataFrame)
                tsheets_df = gr.State(pd.DataFrame())   # list of dataframes for each tsheet.

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


    # ========== Event Handlers ==========