import io
import gradio as gr
import pandas as pd
from metadata import get_gradio_config, get_customers

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

# 2. Upload timesheet.csv file into memory
def upload_tsheet(file_path):

    df = pd.read_csv(file_path)
    return df, df.head(5), gr.update(visible=True) # raw_tsheet, view_raw and btn_submit

# 3. Submit timesheet for processing
def submit_btn(ts):
    from extract_tsheet import clean_raw
    
    # Clean up raw_tsheet
    ts = clean_raw(raw_ts=ts)

    return ts, ts.head(5), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True) # raw_tsheet, view_raw, btn_submit, chkbx_cust, btn_tsheets

# 4. Save selected customer list to state.
def print_values(selected):
    # Update the customers state param with selected customer values
    return selected

# 5. Create timesheet for each customer in customer's state variable.
def tsheets_btn(ts, custs): # Pass in raw_tsheet and customers state variables.
    from extract_tsheet import build_cust_df
    from timesheet_pdf import build_cust_pdf

    # Create timesheet dataframes for customers.
    df_by_cust = {cust: build_cust_df(cust, ts) for cust in custs}

    # Create timesheet pdfs for customers
    pdf_by_cust = {cust: build_cust_pdf(cust, df_by_cust[cust]) for cust in custs}


    return  df_by_cust # tsheet_df, tsheet_files

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

    ########## 
    # SET STATE VARIABLES
    ##########

    customers = gr.State([])    # The list of customers to create individual timesheets and billing files for.

    raw_tsheet = gr.State(pd.DataFrame())   # The master timesheet created from the uploaded csv.
    tsheet_df = gr.State([]) # list of dataframes containing each tsheet.

    tsheet_files = gr.State([]) # list of downloadable files for each customer's tsheet.

    ########## 
    # END STATE VARIABLES
    ##########

    # 1. Create a dataframe by uploading timesheet.csv
    with gr.Group(visible=True) as row_group:
        with gr.Row():
            # Left column: file upload, process button and Customer checkboxes.
            with gr.Column(scale=1, min_width=220):
              raw_csv=gr.File(
                  file_types=['.csv'], type='filepath', 
                  label='Upload Timesheet CSV'
                  )
              
              btn_submit = gr.Button(
                  value='Process',
                  visible=False
                  )
                            
              chkbx_cust = gr.CheckboxGroup(
                  choices=get_customers(),
                  label='Customers',
                  info='Select customers for billing',
                  type='value',
                  interactive=True,
                  visible=False,
                  container=True,                  
              )

              btn_tsheets = gr.Button(
                  value='Create Timesheet',
                  visible=False
              )
              
            # Right column: dataframe view scaled 1: 4
            with gr.Column(scale=4):  
                view_raw=gr.DataFrame(
                    label='Preview (first five rows only). Please review.',
                    wrap=True,
                    )

# End GUI
##########################################################

#---------------------------#

##########################################################
# Event Handlers

            # 1. Create event handler for raw_csv
            raw_csv.change(
                fn=upload_tsheet,
                inputs=raw_csv,
                outputs=[raw_tsheet, view_raw, btn_submit]
            )

            # 3. Submit raw timesheet for processing
            btn_submit.click(
                fn=submit_btn,
                inputs=raw_tsheet,
                outputs=[raw_tsheet, view_raw, btn_submit, chkbx_cust, btn_tsheets]
            )

            # 4. Select customers for billing
            chkbx_cust.change(
                fn=print_values, 
                inputs=chkbx_cust,
                outputs=customers # Update the customers state variable.
            ) # seems to pass a 'selected' param to fn on the backend with the checked values

            # 5. Create Timesheets per customer.
            btn_tsheets.click(
                fn=tsheets_btn,
                inputs=[raw_tsheet, customers],
                outputs=tsheet_df
            )

# End Event Handlers
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