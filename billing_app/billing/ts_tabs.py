import gradio as gr
import pandas as pd
from billing_app.formatter.ts_build import TSFormatter


class TimesheetTabs:
    def __init__(self):
        self.tsf = TSFormatter()

    # ========== Event Functions ==========

    # Upload a csv file for processing
    def ev_file_upload(self, path):

        # Load/format the csv (process_csv should return a filepath or something pd.read_csv can read)
        df = self.tsf.process_csv(path)

        # Build choices for the checkbox immediately
        choices = self._extract_timesheet_choices(df)

        print(f"ev_file_change - rows: {len(df)}")
        print(f"ev_file_change - choices: {len(choices)}")

        return (
            df,                                # ts_view
            gr.update(visible=True),           # ts_buttons
            gr.update(visible=True, choices=choices, value=[])  #chkbox_timesheet
            df,  # working_frame (state variable)
        )

    def _extract_timesheet_choices(self, df: pd.DataFrame):

        from billing_app.db_helper import get_proj_from_jc

        choices = []

        # Quick visibility: what are we actually sending to the DB?
        jcs = df['Job Code'].dropna().unique()
        print(f"_extract_timesheet_choices - unique job codes: {len(jcs)}")
        print(f"_extract_timesheet_choices - sample job codes: {list(jcs[:10])}")

        for jc in jcs:
            # Normalize to plain string for DB lookup
            jc_clean = str(jc).replace("\xa0", " ").strip()

            rows = get_proj_from_jc(jc_clean)
            if len(rows) == 0:
                print(f"NO MATCH for job code: [{jc_clean}]")
            else:
                for item in rows:
                    choices.append(f"{item['client']} - {item['proj']}")

        return choices
    # ========== UI Builders ==========
    def build_ts_tab(self, parent):
        with parent:
            gr.Markdown(
                "### Upload your full Tsheet csv file. Make sure the dates on the file match your billing dates."
            )

            with gr.Tab("Timesheets"):
                # Declare state variables (keep if you need later)
                # cur_df = gr.State(pd.DataFrame())
                # tsheets_df = gr.State(pd.DataFrame())
                working_frame = gr.State(pd.Dataframe())

                with gr.Row():
                    with gr.Column(scale=1, min_width=220):
                        file = gr.File(
                            file_types=[".csv"],
                            type="filepath",
                            label="Upload Raw TSheet (csv)",
                        )

                        chkbx_timesheet = gr.CheckboxGroup(
                            choices=[],
                            info="Select customers for billing",
                            type="value",
                            interactive=True,
                            visible=False,
                            container=True,
                        )

                        ts_buttons = gr.Group(visible=False)
                        with ts_buttons:
                            btn_t_ok = gr.Button("OK")
                            with gr.Row():
                                btn_t_back = gr.Button("<-", interactive=False)
                                btn_t_next = gr.Button("->", interactive=False)

                    with gr.Column(scale=5):
                        ts_view = gr.DataFrame(wrap=True)

                # ========== Event Wiring ==========
                file.upload(
                    fn=self.ev_file_upload,
                    inputs=[file],
                    outputs=[
                        ts_view,
                        ts_buttons,
                        chkbx_timesheet,
                        working_frame,
                    ],
                )

                btn_t_ok.click(
                    fn=self.ev_btn_t_ok_click,
                    inputs=[chkbx_timesheet]
                )