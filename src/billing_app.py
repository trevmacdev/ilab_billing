import io
import gradio as gr
import pandas as pd
from metadata import get_gradio_config

'''
Algorythm:
1. Display file upload to user > Load timesheet file into memory.
2. Display the timesheet as a raw dataframe and let the user confirm.
3. Create a new dataframe using the raw dataframe, processing it with extract_tsheet.py
4. Allow the user to select customers for timesheet and billing file creation -> save to state
5. Create timesheet per customer
6. Allow user to set the default download path for each customer's billing files (extract from config.properties)
7. Display timesheet per customer in tab with a download button -> pdf the timesheet and download the file.
8. Create and display billing files in tabs with a download button -> xlsx the spreadsheet and downoad the billing file.
'''

##########################################################
# Functions

# 1. Upload timesheet.csv file into memory
def upload_tsheet(file_path):

    df = pd.read_csv(file_path)
    return df, df.head(5), gr.update(visible=True) # raw_tsheet, view_raw and btn_submit

# 1. Submit timesheet for processing
def create_cust_tsheets(ts):
    from extract_tsheet import clean_raw
    
    # Clean up raw_tsheet
    ts = clean_raw(raw_ts=ts)
    
    return ts, ts.head(5) # raw_tsheet, view_raw

# End Functions
##########################################################

#----------------------#

##########################################################
# GUI
with gr.Blocks(title='Billing App') as billing_app:
    # Page header
    gr.Markdown('# iLAB Billing App')
    gr.Markdown('Export a timesheet in .csv format, from the Project Reports in TSheets.')
    gr.Markdown("Don't worry about filtering names, just make sure your start and end dates are correct.")

    # Set state variables
    raw_tsheet = gr.State(pd.DataFrame())

    # 1. Create a dataframe by uploading timesheet.csv
    with gr.Group(visible=True) as row_group:
        with gr.Row():
            # Left column: file upload + process button
            with gr.Column(scale=1, min_width=220):
              raw_csv=gr.File(
                  file_types=['.csv'], type='filepath', 
                  label='Upload Timesheet CSV'
                  )
              
              btn_submit = gr.Button(
                  value='Process',
                  visible=False
                  )

            # Right column: dataframe view scaled 1: 4
            with gr.Column(scale=4):  
                view_raw=gr.DataFrame(
                    label='Preview (first five rows only). Please review.',
                    wrap=True
                    )

            # 1. Create event handler for raw_csv
            raw_csv.change(
                fn=upload_tsheet,
                inputs=raw_csv,
                outputs=[raw_tsheet, view_raw, btn_submit]
            )

            # 1. Submit timesheet for processing
            btn_submit.click(
                fn=create_cust_tsheets,
                inputs=raw_tsheet,
                outputs=[raw_tsheet, view_raw]
            )





# End GUI
##########################################################



####
#   START SERVER
####

gradio_config = get_gradio_config()

if __name__ == '__main__':
    billing_app.launch(
        server_name=gradio_config['server_name'],
        server_port=gradio_config['server_port'],
        show_error=gradio_config['show_error'],
        share=gradio_config['share'],
        show_api=gradio_config['show_api'],
    )