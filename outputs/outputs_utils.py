import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.graph_objects as go
import numpy as np


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


def generate_bar_chart(
        df_summary_output,
        selected_date,
        column_names,
        category_column,
        columns_label,
        marker_color,
        title,
        yaxis_title,
        margin_l=50,
        margin_r=50,
        margin_t=50,
        margin_b=50,
):

    # Functions
    data = {
        category_column: column_names,
        columns_label: df_summary_output[df_summary_output['Period'] == selected_date][column_names].values[0],
    }
    df = pd.DataFrame(data)

    # Initiate Figure
    fig = go.Figure()

    # Add Prior amounts
    fig.add_trace(go.Bar(
        x=df[category_column],
        y=df[columns_label],
        name=columns_label,
        marker_color=marker_color
    ))

    # Update the layout
    fig.update_layout(
        title=title,
        barmode='overlay',  # Using overlay to allow manual stacking and handling of bases
        xaxis_title=category_column,
        yaxis_title=yaxis_title
    )

    fig.update_layout(
        margin=dict(
            l=margin_l,
            r=margin_r,
            t=margin_t,
            b=margin_b
        )  # Adjust bottom margin to give more space for x-axis labels
    )

    return fig


def column_pos_and_neg_movements_chart(
        df,
        category_column,
        prior_label,
        movement_label,
        title,
        yaxis_title,
        marker_color_prior='lightblue',
        marker_color_positive='blue',
        marker_color_negative='red',
        margin_l=50,
        margin_r=50,
        margin_t=50,
        margin_b=50,
        legend_x=0.5,
        legend_y=1.05,
):
    # Assign positive and negative movements
    movement_label_positive = "Positive " + movement_label
    movement_label_negative = "Negative " + movement_label
    df[movement_label_positive] = np.where(df[movement_label] >= 0, df[movement_label], 0)
    df[movement_label_negative] = np.where(df[movement_label] < 0, df[movement_label], 0)

    # Initiate Figure
    fig = go.Figure()

    # Add Prior amounts
    fig.add_trace(go.Bar(
        x=df[category_column],
        y=df[prior_label],
        name=prior_label,
        marker_color=marker_color_prior
    ))

    # Add Positive Movements
    fig.add_trace(go.Bar(
        x=df[category_column],
        y=df[movement_label_positive],
        name=movement_label_positive,
        marker_color=marker_color_positive,
        base=df[prior_label]  # This starts the positive movements right on top of the prior amounts
    ))

    # Add Negative Movements
    fig.add_trace(go.Bar(
        x=df[category_column],
        y=df[movement_label_negative],
        name=movement_label_negative,
        marker_color=marker_color_negative,
        # base=df[prior_label]  # This starts the negative movements at the top of the prior amounts
        base=df[prior_label]*0  # This starts the negative movements at the top of the prior amounts
    ))

    # Update the layout
    fig.update_layout(
        title=title,
        barmode='overlay',  # Using overlay to allow manual stacking and handling of bases
        xaxis_title=category_column,
        yaxis_title=yaxis_title
    )
 
    fig.update_layout(
        legend=dict(
            x=legend_x,
            y=legend_y,  # Places the legend above the plot
            xanchor='center',
            orientation='h'
        )
    )

    fig.update_layout(
        margin=dict(
            l=margin_l,
            r=margin_r,
            t=margin_t,
            b=margin_b
        )  # Adjust bottom margin to give more space for x-axis labels
    )
    
    return fig


def generate_pos_neg_charts(
        df_summary_output,
        column_names,
        reference_dates,
        category_column,
        grouping_name, # E.g. 'Loan', 'Deposit'
):
    # Initiate dictionary
    pos_neg_charts = {}

    # Generate Loan Movements by Category bar charts
    for reference_date, date_details in reference_dates.items():
        # Labels
        prior_label = f"Total {date_details['name']} ago"
        movement_label = f"{date_details['name']} Movement"

        # Create movement column names list
        movement_column_names = [name + " - movement" for name in column_names]

        # Create data to be charted
        data = {
            category_column: column_names,
            prior_label: df_summary_output[df_summary_output['date_reference'] == reference_date][column_names].values[0],
            movement_label: df_summary_output[df_summary_output['date_reference'] == reference_date][movement_column_names].values[0],
        }
        df = pd.DataFrame(data)

        pos_neg_charts[f"{grouping_name.lower()}_pos_neg_chart_{reference_date}"] = column_pos_and_neg_movements_chart(
            df=df,
            category_column=category_column,
            prior_label=prior_label,
            movement_label=movement_label,
            title=f"{grouping_name} Movements by Category - movements over {date_details['name']}",
            yaxis_title=f"{grouping_name} Amount",
            marker_color_prior='lightblue',
            marker_color_positive='blue',
            marker_color_negative='red',
            margin_l=50,
            margin_r=200,
            margin_t=50,
            margin_b=180,
            legend_x=0.5,
            legend_y=1.05,
        )

    return pos_neg_charts