import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta


def get_month_end_x_months_ago(current_date, months_ago):
    """
    Calculates the month-end date for 'months_ago' months before 'current_date',
    returning only the date component (year, month, day).

    Parameters:
    current_date (str or datetime): The date from which to calculate.
    months_ago (int): The number of months to go back.

    Returns:
    datetime: The month-end date 'months_ago' months before 'current_date', with no time component.
    """
    # Convert current_date to datetime if it is not already
    if isinstance(current_date, str):
        current_date = pd.to_datetime(current_date)
    
    # Calculate the date 'months_ago' months before the current_date
    target_date = current_date - relativedelta(months=months_ago)
    
    # Get the month end for the target date, and normalize to remove time component
    month_end_date = pd.to_datetime(target_date).to_period('M').to_timestamp(how='end').normalize()
    
    return month_end_date

def determine_reference_dates(selected_date, available_dates, date_periods):
    """
    Determines the most appropriate reference dates based on a given date and a set of available dates.
    This function recursively selects reference dates from predefined periods, using a cascading fallback
    mechanism if the preferred reference date is not available in the provided dates.

    Parameters:
    - selected_date (datetime): The date from which the reference periods are calculated. This is 
                                the base date used to compute historical reference dates.
    - available_dates (set or list): A collection of dates that are available for referencing. The function
                                     checks if computed reference dates exist within this collection.
    - date_periods (dict): A dictionary where each key is an integer representing the number of months
                           ago from the selected_date for which to find a reference date. Each key maps to
                           a dictionary containing:
                           - 'info': A dictionary with details about the period (e.g., name, description).
                           - 'fallback': A nested dictionary that follows the same structure, representing
                                         the next fallback if the initial period's reference date is unavailable.

    Returns:
    - dict: A dictionary where keys are datetime objects of the successfully determined reference dates,
            and values are the 'info' dictionaries from date_periods corresponding to each date. If no
            dates are found, the function returns None.

    Example of usage:
    date_periods = {
        60: {'info': {'name': '5 years ago', 'over_period': 'over the past 5 years'}, 'fallback': {...}}
    }
    reference_dates = determine_reference_dates(pd.to_datetime('2023-12-31'), available_dates, date_periods)
    """
    reference_dates_dict = {}
    for period_name, info_and_fallback in date_periods.items():
        reference_date = get_month_end_x_months_ago(selected_date, info_and_fallback['info']['months_int'])
        if reference_date in available_dates:
            info_and_fallback['info']['date'] = reference_date
            reference_dates_dict[period_name] = info_and_fallback['info']
        elif info_and_fallback['fallback'] is not None:
            ret = determine_reference_dates(selected_date, available_dates, info_and_fallback['fallback'])
            if ret:
                reference_dates_dict.update(ret)
        else:
            st.error(f"Error: All 4 date references must be present.")
            st.error(f"Please makke another selection")
            st.stop()

    return reference_dates_dict if reference_dates_dict else None


def generate_reference_dates(
        df,
        date_column,
        selected_date,
        reference_dates_config,
):
    ret_dict = determine_reference_dates(
        selected_date=selected_date,
        available_dates=set(df[date_column]),
        date_periods=reference_dates_config,
    )

    return ret_dict
