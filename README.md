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

