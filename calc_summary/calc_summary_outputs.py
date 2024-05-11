import logging
import os
import pickle

import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

from calc_summary.summary_utils import determine_reference_dates
from calc_summary.summerise_loans import generate_summary_loans_dict
from calc_summary.summerise_deposits import generate_summary_deposits_dict
from utils import movement_text, dollar_movement_text, rounded_dollars

logger = logging.getLogger(__name__)

def generate_df_summary_output(
        df_summary,
        date_column,
        selected_date,
        reference_dates,
):
    # Obtain reference dates
    dates_list = []
    for key in reference_dates.keys():
        dates_list = dates_list + [reference_dates[key]['date']]
    dates_list = [selected_date] + dates_list

    # Filter the DataFrame for rows where the date is one of the reference dates or the selected_date
    df_summary_output = df_summary[df_summary[date_column].isin(dates_list)].copy()

    # Sort the DataFrame by Period for better visualization and to ensure calculations are done correctly
    df_summary_output.sort_values(date_column, inplace=True)

    # Find the row for the selected_date
    selected_date_row = df_summary_output[df_summary_output[date_column] == selected_date]

    # For each column (except 'Period'), calculate the movement and create a new column
    for column in df_summary_output.columns:
        if column != date_column:  # Skip the 'Period' column
            # Calculate the difference from each row to the value at selected_date for this column
            df_summary_output[column + ' - movement'] = selected_date_row[column].values[0] - df_summary_output[column]

    for key, value in reference_dates.items():
        df_summary_output.loc[df_summary_output['Period'] == value['date'], 'date_reference'] = key
    df_summary_output.loc[df_summary_output['Period'] == selected_date, 'date_reference'] = 'selected_date'

    return df_summary_output


def generate_summary_outputs(
        df_summary,
        pkl_folder_name,
        date_column,
        selected_date,
        top_x_value,
        outputs_config_dict,
):
    logger.info("Executing: generate_summary_outputs")

    # Set pickle variable path
    summary_dict_pkl=os.path.join(
        pkl_folder_name,
        f"summary_pickle-{date_column}-{selected_date}-{top_x_value}.pkl"
    )

    # Check if summary data already exists and load it, otherwise create the data
    if os.path.exists(summary_dict_pkl):
        # Data exists, load it from pickle
        logger.info("Loading summary from pickle files")

        # Load df original data
        with open(summary_dict_pkl, 'rb') as f:
            summary_dict = pickle.load(f)

    else:
        logger.info("Creating summary data")

        # Generate reference dates
        reference_dates = determine_reference_dates(
            selected_date=selected_date,
            available_dates=set(df_summary[date_column]),
            date_periods=outputs_config_dict['reference_dates_config'],
        )

        # Create the summary output df for the selected date
        df_summary_output = generate_df_summary_output(
            df_summary=df_summary,
            date_column=date_column,
            selected_date=selected_date,
            reference_dates=reference_dates,
        )

        # Initialise summary dictionary
        summary_dict = {}

        # Generate Loan Summary Dict for selected date
        summary_dict['summary_loans_dict'] = generate_summary_loans_dict(
            df_summary_output=df_summary_output,
            date_column=date_column,
            selected_date=selected_date,
            reference_dates=reference_dates,
        )

        # Generate Deposit Summary Dict for selected date
        summary_dict['summary_deposits_dict'] = generate_summary_deposits_dict(
            df_summary_output=df_summary_output,
            date_column=date_column,
            selected_date=selected_date,
            reference_dates=reference_dates,
        )

        # Add values to the dictionary
        summary_dict['reference_dates'] = reference_dates
        summary_dict['df_summary_output'] = df_summary_output

        # Write summary dictionary to pickle file
        with open(summary_dict_pkl, 'wb') as f:
            pickle.dump(summary_dict, f)

    return summary_dict