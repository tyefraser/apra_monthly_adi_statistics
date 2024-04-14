import logging
import pandas as pd
import streamlit as st
import numpy as np
import datetime as dt

logger = logging.getLogger(__name__)


def date_selection(
        df,
        date_column,
        col1,
):
    # Extract unique values from the column for dropdown options
    complete_dates_list = sorted(list(df[date_column].unique()), reverse=True)

    # Convert to datetime.datetime object
    complete_dates_list = pd.to_datetime(complete_dates_list).to_pydatetime()

    # Convet list to strings to present in list
    complete_dates_list_str = [
        timestamp.strftime('%Y %B %d') for timestamp in complete_dates_list]
        
    # max date from df
    max_date = complete_dates_list_str[0]

    # Create a dropdown widget with the unique values from the column
    # Place a selectbox in each column
    with col1:
        selected_date_picked = st.selectbox('Date', complete_dates_list_str, index=complete_dates_list_str.index(max_date))

    selected_date = complete_dates_list[complete_dates_list_str.index(selected_date_picked)]

    return selected_date


def company_selection(
        df,
        date_column,
        selected_date,
        company_column,
        default_company,
        col3,
):
    """Select Company to track in the output"""

    # Extract unique values from the column for dropdown options for the date selected
    categories = list(df[df[date_column] == selected_date][company_column].unique())
    
    # Set a default selected value for the dropdown, if it exists
    default_company = default_company if default_company in categories else categories[0]

    # Create a dropdown widget with the unique values from the column
    with col3:
        selected_company = st.selectbox('Select ' + company_column, categories, index=categories.index(default_company))
    
    return selected_company


def top_x_selection(
        df,
        date_column,
        selected_date,
        company_column,
        default_x_value = None,
):

    company_list_for_month = df[df[date_column] == selected_date][company_column].unique()

    # Define default_x_value if not set
    if default_x_value == None:
        default_x_value=int(len(company_list_for_month)/5)

    # Create a slider widget with the unique values from the column
    top_x_value = st.slider('Select Top x', 1, len(company_list_for_month), default_x_value, 1)

    return top_x_value


def select_data_filters(
        df,
        date_column,
        company_column,
        default_company
):
    """
    This returns the filter selections made to apply to the data.
    Note: The filtering could be, but isnt, performed here for a number of reasons.
    """
    logger.debug("Executing: select_data_filters")

    # Create three columns to display the dropdowns
    col1, col3 = st.columns(2)

    # Filter for the selected date
    selected_date = date_selection(
        df=df,
        date_column=date_column,
        col1=col1,
    )

    # Select company
    selected_company = company_selection(
        # only select categories from the relevant date selected
        df=df,
        date_column=date_column,
        selected_date=selected_date,
        company_column=company_column,
        default_company=default_company,
        col3=col3,
    )

    # Select top x
    top_x_value = top_x_selection(
        df=df,
        date_column=date_column,
        selected_date=selected_date,
        company_column=company_column,
        default_x_value = 15,
    )

    logger.debug("Executed: select_data_filters")
    return selected_date, selected_company, top_x_value
