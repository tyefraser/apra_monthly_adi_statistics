import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

from output_utils import determine_reference_dates
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

def generate_summary_housing_info(
        df_summary_output,
        date_column,
        selected_date,
        reference_dates,
        df_summary_1_month,
        df_summary_6_months,
        df_summary_12_months,
        df_summary_long_term,
):
    # Initiate summary charts and info dict 
    summary_housing_info = {}

    # Get data for selected date
    df_summary_output_selected_date = df_summary_output[df_summary_output[date_column] == selected_date]


    # Data elements for property percentages pie chart
    data = {
        'Property Type': ['Investment Property', 'Owner-occupied Property'],
        'Percentage': [
            df_summary_output_selected_date['Loans to Housing: Investment Property Percentage'].values[0],
            df_summary_output_selected_date['Loans to Housing: Owner-occupied Property Percentage'].values[0]
        ]
    }
    # Create the pie chart
    fig = px.pie(
        data,
        names='Property Type',
        values='Percentage',
        title='Distribution of Loans to Housing Property Types',
        color='Property Type',  # Field to define the colors
        color_discrete_map={  # Assigns specific colors
            'Investment Property': '#ff9999',
            'Owner-occupied Property': '#66b3ff'
        }
    )
    summary_housing_info['housing_percentages_pie'] = fig

    # Period Movements - text
    for period, descriptors in reference_dates.items():
        over_period = descriptors['over_period']
        investment_movement = df_summary_output.loc[df_summary_output['date_reference'] == period, 'Loans to households: Housing: Investment - movement'].values[0]
        oo_movement = df_summary_output.loc[df_summary_output['date_reference'] == period, 'Loans to households: Housing: Owner-occupied - movement'].values[0]
        summary_housing_info[f"housing_oo_i_movements_{period}"] = (
            over_period + " owner-occupiedd loans have " + dollar_movement_text(dollar_movement=oo_movement) +
            ", whilst investment property loans have " + dollar_movement_text(dollar_movement=investment_movement) + "."
        )
    
    # Period Movements - table
    over_period = []
    investment_movements = []
    oo_movement = []
    for period, descriptors in reference_dates.items():
        over_period.append(reference_dates[period]['name'])
        investment_movements.append(rounded_dollars(dollars=df_summary_output.loc[df_summary_output['date_reference'] == period, 'Loans to households: Housing: Investment - movement'].values[0]))
        oo_movement.append(rounded_dollars(dollars=df_summary_output.loc[df_summary_output['date_reference'] == period, 'Loans to households: Housing: Owner-occupied - movement'].values[0]))
    movements_table = pd.DataFrame({
        "Period": over_period,
        "Owner-Occupied Loans Increase": oo_movement,
        "Investment Property Loans Increase": investment_movements,
    })

    # Reset the index and drop it
    movements_table.reset_index(drop=True, inplace=True)
    summary_housing_info['movements_table'] = movements_table
    

    # Period movements - monthly averages
    data = {
        'Period': [
            reference_dates['1_month']['name'],
            reference_dates['6_months']['name'],
            reference_dates['12_months']['name'],
            reference_dates['long_term']['name'],
        ],
        'Investment loans movement': [
            df_summary_1_month['Loans to households: Housing: Investment - movement'].values[0] / reference_dates['1_month']['months_int'],
            df_summary_6_months['Loans to households: Housing: Investment - movement'].values[0] / reference_dates['6_months']['months_int'],
            df_summary_12_months['Loans to households: Housing: Investment - movement'].values[0] / reference_dates['12_months']['months_int'],
            df_summary_long_term['Loans to households: Housing: Investment - movement'].values[0] / reference_dates['long_term']['months_int'],
        ],
        'Owner-occupied loans movement': [
            df_summary_1_month['Loans to households: Housing: Owner-occupied - movement'].values[0] / reference_dates['1_month']['months_int'],
            df_summary_6_months['Loans to households: Housing: Owner-occupied - movement'].values[0] / reference_dates['6_months']['months_int'],
            df_summary_12_months['Loans to households: Housing: Owner-occupied - movement'].values[0] / reference_dates['12_months']['months_int'],
            df_summary_long_term['Loans to households: Housing: Owner-occupied - movement'].values[0] / reference_dates['long_term']['months_int'],
        ],
    }

    # Create the figure object
    fig = go.Figure()

    # Add bars for investment data
    fig.add_trace(go.Bar(
        x=data['Period'],
        y=data['Investment loans movement'],
        name='Investment loans movement',  # Legend entry
        marker_color='#ff9999'  # Color of the bar
    ))

    # Add bars for owner-occupied data
    fig.add_trace(go.Bar(
        x=data['Period'],
        y=data['Owner-occupied loans movement'],
        name='Owner-occupied loans movement',
        marker_color='#66b3ff'  # Color of the bar
    ))

    # Update the layout for a grouped bar chart
    fig.update_layout(
        title='Investment and Owner-occupied Property Loans - monthly averages',
        xaxis_title='Period',
        yaxis_title='Average Monthly Movement',
        barmode='group',  # Group bars of different traces at each x value
        xaxis_tickangle=-45,  # Rotate labels for better readability
        legend=dict(
            orientation="h",  # 'h' for horizontal (default is 'v' for vertical)
            xanchor="center",  # Anchor point
            x=0.5,  # Center the legend horizontally
            y=-0.3  # Position the legend below the x-axis
        )
    )

    summary_housing_info['housing_movements_annualised'] = fig

    return summary_housing_info
    

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

    # Generate individual dfs for each date
    df_summary_1_month = df_summary_output[df_summary_output[date_column] == reference_dates['1_month']['date']]
    df_summary_6_months = df_summary_output[df_summary_output[date_column] == reference_dates['6_months']['date']]
    df_summary_12_months = df_summary_output[df_summary_output[date_column] == reference_dates['12_months']['date']]
    df_summary_long_term = df_summary_output[df_summary_output[date_column] == reference_dates['long_term']['date']]

    # Initialise summary dictionary
    summary_dict = {}

    # Generate df_summary_output for selected date
    summary_dict['summary_housing_info'] = generate_summary_housing_info(
        df_summary_output=df_summary_output,
        date_column=date_column,
        selected_date=selected_date,
        reference_dates=reference_dates,
        df_summary_1_month=df_summary_1_month,
        df_summary_6_months=df_summary_6_months,
        df_summary_12_months=df_summary_12_months,
        df_summary_long_term=df_summary_long_term,
    )

    
    # Add values to the dictionary
    summary_dict['reference_dates'] = reference_dates
    summary_dict['df_summary_output'] = df_summary_output
    
    return summary_dict