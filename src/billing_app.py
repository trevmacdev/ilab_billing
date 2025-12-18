
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
    5.1 Allow user to select working customer.
6. Allow user to set the default download path for each customer's billing files (extract from config.properties)
7. Display timesheet per customer in tab with a download button -> pdf the timesheet and download the file.
8. Create and display billing files in tabs with a download button -> xlsx the spreadsheet and downoad the billing file.
'''

##########################################################
# Functions

# 2. Upload timesheet.csv file into memory
def upload_tsheet(file_path):

    df = pd.read_csv(file_path)
    return (
        df,                     # raw_tsheet
        df.head(5),             # view_output
        gr.update(visible=True) # btn_submit
        )

# 3. Submit timesheet for processing
def submit_btn(ts):
    from extract_tsheet import clean_raw
    
    # Clean up raw_tsheet
    ts = clean_raw(raw_ts=ts)

    return (
        ts,                         # raw_tsheet
        ts.head(5),                 # view_output
        gr.update(visible=False),   # btn_submit
        gr.update(visible=True),    # chkbx_cust
        gr.update(visible=True)     # btn_tsheets
        )

# 4. Save selected customer list to state.
def print_values(selected):
    # Update the customers state param with selected customer values
    return selected

# 5. Create timesheet for each customer in customer's state variable.
def tsheets_btn(ts, custs): # Pass in raw_tsheet and customers state variables.
    # Don't bother if there are no customers selected.
    if not custs:
        return
    
    # Import dependencies to build timesheet dataframes and pdfs.
    from extract_tsheet import build_cust_df
    from timesheet_pdf import build_cust_pdf

    # Create timesheet dataframes for customers.
    df_by_cust = {cust: build_cust_df(cust, ts) for cust in custs}
    first_df = df_by_cust[custs[0]]

    # Duplicate the first dataframe in df_by_cust to pass to view_outputs

    # Create timesheet pdfs for customers
    pdf_by_cust = {cust: build_cust_pdf(cust, df_by_cust[cust]) for cust in custs}

    # Update Label above output view.
    label = gr.Markdown(f'### Timesheet: {custs[0]}')

    return(
        custs[0],                       # curr_cust
        df_by_cust,                     # tsheet_df
        first_df,                       # view_output
        gr.update(visible=False),       # chkbx_cust
        gr.update(visible=False),       # btn_tsheets
        gr.update(visible=True),        # btn_download
        gr.Row.update(visible=True),    # nav_buttons
        label                           # view_output_label
        )  

def back_btn(
        cust,       # curr_cust_state variable
        ts          # tsheet_df state variable
        ):
    
    # We pass in the currently viewed customer and the dictionary of customer timesheets.
    # We then cycle backwards through the ts dict, going to the end if we're already at the start.

    # Create an index for the keys in ts.
    ts_keys = list(ts.keys())
    index = ts_keys.index(cust)

    # If there is only one customer in ts, do nothing.
    if len(ts_keys) == 1:
        return

    # If we are on the first customer in ts, go to the last. Else go to previous customer
    if index == 0:
        index = len(ts_keys) - 1
    else:
        index = index - 1

    # update cust value with new index.
    cust = ts_keys[index]

    # retieve dataframe for previous customer.
    df = ts[cust]

    # Update Label above output view.
    label = gr.Markdown(f'### Timesheet: {cust}')

    return(
        cust,   # curr_cust,
        df,     # view_output
        label   # view_output_label
    )

def next_btn(
        cust,       # curr_cust_state variable
        ts          # tsheet_df state variable
        ):
    
    # We pass in the currently viewed customer and the dictionary of customer timesheets.
    # We then cycle backwards through the ts dict, going to the end if we're already at the start.

    # Create an index for the keys in ts.
    ts_keys = list(ts.keys())
    index = ts_keys.index(cust)

    # If there is only one customer in ts, do nothing.
    if len(ts_keys) == 1:
        return

    # If we are on the last customer in ts, go to the first. Else go to next customer
    if index == len(ts_keys) - 1:
        index = 0
    else:
        index = index + 1

    # update cust value with new index.
    cust = ts_keys[index]

    # retieve dataframe for previous customer.
    df = ts[cust]

    # Update Label above output view.
    label = gr.Markdown(f'### Timesheet: {cust}')

    return(
        cust,   # curr_cust,
        df,     # view_output
        label   # view_output_label
    )

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

    curr_cust = gr.State()   # hold the name of the currently viewed customer.

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

              # 5.1 Add back and next buttons to cycle through   
              with gr.Row(visible=False) as nav_buttons:
                  btn_back = gr.Button(
                      value='Back'
                  )

                  btn_next = gr.Button(
                      value='Next'
                  )

              btn_download = gr.Button(
                  value='Download Timesheet PDF',
                  visible=False
              )

            # Right column: dataframes in tabs
            with gr.Column(scale=4):
                view_output_label = gr.Markdown(f'### Timesheet: Raw')
                view_output=gr.DataFrame(
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
        outputs=[raw_tsheet, view_output, btn_submit]
    )

    # 3. Submit raw timesheet for processing
    btn_submit.click(
        fn=submit_btn,
        inputs=raw_tsheet,
        outputs=[
            raw_tsheet, 
            view_output, 
            btn_submit, 
            chkbx_cust, 
            btn_tsheets
            ]
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
        outputs=[
            curr_cust,
            tsheet_df, 
            view_output, 
            chkbx_cust, 
            btn_tsheets, 
            btn_download, 
            nav_buttons,
            view_output_label
        ]
    )

    # 5.1 Navigate through views 
    btn_back.click(
        fn=back_btn,
        inputs=[
            curr_cust, 
            tsheet_df,
        ],
        outputs=[
            curr_cust,
            view_output,
            view_output_label
        ]
    )

    btn_next.click(
        fn=next_btn,
        inputs=[
            curr_cust, 
            tsheet_df,
        ],
        outputs=[
            curr_cust,
            view_output,
            view_output_label
        ]
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