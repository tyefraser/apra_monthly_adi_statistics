# APRA Monthly ADI Statistics (MADIS) Report
Thie repo is used to generate the APRA MADIS reporting tool to visualise movement in the banking industry. The website should be available online at **TO create URL** for general useage. The below section will detail information about the repo and how to sue it.

## Setup
To run the code locally, you will need to:
* Download the repo from the repository
* Create the virtual environment and load the libraries
    * cd **repo**
    * python -m venv venv
    * Activate the venv:
      For windows:
      venv\Scripts\activate
      :For linux/gitbash
      source venv/Scripts/activate # 
    * %pip install -r requirements.txt
* Run the streamlit app:
    streamlit run streamlit_app.py



# Processing Details
This sections will run through how the app run from start to end.

## steamlit_app.py
The `steamlit_app.py` is the main entry point to initiate the code. This is where all of the processes are orchestrated for everything to work.


File link as at 2024-09-11:
Actual: https://www.apra.gov.au/sites/default/files/2024-08/20240830%20-%20Monthly%20authorised%20deposit-taking%20institution%20statistics%20July%202024.xlsx
Coded:  https://www.apra.gov.au/sites/default/files/2024-08/Monthly%20authorised%20deposit-taking%20institution%20statistics%20back-series%20March%202019%20-%20.xlsx
Code:
base_url = 'https://www.apra.gov.au/sites/default/files/'
    last_month_eom = datetime.now().replace(day=1) - timedelta(days=1)
    last_month_yyyy_mm = last_month_eom.strftime('%Y-%m')
    file_path = '/Monthly%20authorised%20deposit-taking%20institution%20statistics%20back-series%20March%202019%20-%20'
    two_months_ago = last_month_eom - relativedelta(months=1)
    two_months_ago_mmm_yyyy = two_months_ago.strftime('%B %Y')
    file_extension = '.xlsx'

    # Concatenate the strings to form the full URL
    full_url = base_url + last_month_yyyy_mm + file_path + quote(two_months_ago_mmm_yyyy) + file_extension
This needs to be updated
