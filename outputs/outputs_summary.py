import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

from outputs.outputs_utils import determine_reference_dates
from outputs.outputs_summary_loans import generate_summary_loans_dict
from outputs.outputs_summary_deposits import generate_summary_deposits_dict
from utils import movement_text, dollar_movement_text, rounded_dollars

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
        date_column,
        selected_date,
        top_x_value,
        outputs_config_dict,
):
    # Get pickle file name
    summary_dict_pickle = f"summary_pickle-{date_column}-{selected_date}"

    # To do: Load from pickle if the exact same version already exists
    # Else create a new pickle and dict

    

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
    
    return summary_dict