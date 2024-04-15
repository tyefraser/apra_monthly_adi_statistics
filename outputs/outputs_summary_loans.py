import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

from outputs.outputs_utils import determine_reference_dates
from outputs.outputs_utils import column_pos_and_neg_movements_chart
from outputs.outputs_utils import generate_bar_chart
from outputs.outputs_utils import generate_pos_neg_charts
from utils import movement_text, dollar_movement_text, rounded_dollars

def generate_housing_percentages_pie(
        df_summary_output,
        date_column,
        selected_date,
):
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
    
    return fig


def generate_loan_pos_neg_charts(
        df_summary_output,
        loan_column_names,
        reference_dates,
        category_column,
):
    # Initiate dictionary
    loan_pos_neg_charts = {}

    # Generate Loan Movements by Category bar charts
    for reference_date, date_details in reference_dates.items():
        # Labels
        prior_label = f"Total {date_details['name']} ago"
        movement_label = f"{date_details['name']} Movement"

        # Create movement column names list
        loan_movement_column_names = [name + " - movement" for name in loan_column_names]

        # Create data to be charted
        data = {
            category_column: loan_column_names,
            prior_label: df_summary_output[df_summary_output['date_reference'] == reference_date][loan_column_names].values[0],
            movement_label: df_summary_output[df_summary_output['date_reference'] == reference_date][loan_movement_column_names].values[0],
        }
        df = pd.DataFrame(data)

        loan_pos_neg_charts[f"loan_pos_neg_chart_{reference_date}"] = column_pos_and_neg_movements_chart(
            df=df,
            category_column=category_column,
            prior_label=prior_label,
            movement_label=movement_label,
            title=f"Loan Movements by Category - movements over {date_details['name']}",
            yaxis_title='Loan Amount',
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

    return loan_pos_neg_charts


def generate_summary_loans_dict(
        df_summary_output,
        date_column,
        selected_date,
        reference_dates,
):
    # Initiate summary charts and info dict 
    summary_loans_dict = {}

    # List the loan columns
    loan_column_names = [
        "Loans to non-financial businesses",
        "Loans to financial institutions",
        "Loans to general government",
        "Loans to households: Housing: Owner-occupied",
        "Loans to households: Housing: Investment",
        "Loans to households: Credit cards",
        "Loans to households: Other",
        "Loans to community service organisations",
    ]

    # Generate bar chart for Loan Totals
    summary_loans_dict["loan_totals_bar_chart"] = generate_bar_chart(
        df_summary_output=df_summary_output,
        selected_date=selected_date,
        column_names=loan_column_names,
        category_column='Loan Category',
        columns_label = 'Total Loan Amount',
        marker_color='lightblue',
        title=f"Loan Category Totals as at {selected_date.strftime('%d %B %Y')}",
        yaxis_title='Total Loan Amount',
        margin_l=50,
        margin_r=200,
        margin_t=50,
        margin_b=180,
    )
    
    ## # Generate Loans positive and negative movements charts
    ## summary_loans_dict['loan_pos_neg_charts'] = generate_loan_pos_neg_charts(
    ##     df_summary_output=df_summary_output,
    ##     loan_column_names = loan_column_names,
    ##     reference_dates=reference_dates,
    ##     category_column='Loan Category',
    ## )
    # Generate Deposit positive and negative movements charts
    summary_loans_dict['loan_pos_neg_charts'] = generate_pos_neg_charts(
        df_summary_output=df_summary_output,
        column_names=loan_column_names,
        reference_dates=reference_dates,
        category_column='Loan Category',
        grouping_name='Loan',
    )

    # Generate housing percentage pic chart
    summary_loans_dict['housing_percentages_pie'] = generate_housing_percentages_pie(
        df_summary_output,
        date_column,
        selected_date,
    )

    ## # Period Movements - text
    ## for period, descriptors in reference_dates.items():
    ##     over_period = descriptors['over_period']
    ##     investment_movement = df_summary_output.loc[df_summary_output['date_reference'] == period, 'Loans to households: Housing: Investment - movement'].values[0]
    ##     oo_movement = df_summary_output.loc[df_summary_output['date_reference'] == period, 'Loans to households: Housing: Owner-occupied - movement'].values[0]
    ##     summary_loans_dict[f"housing_oo_i_movements_{period}"] = (
    ##         over_period + " owner-occupiedd loans have " + dollar_movement_text(dollar_movement=oo_movement) +
    ##         ", whilst investment property loans have " + dollar_movement_text(dollar_movement=investment_movement) + "."
    ##     )
    ## 
    ## # Period Movements - table
    ## over_period = []
    ## investment_movements = []
    ## oo_movement = []
    ## for period, descriptors in reference_dates.items():
    ##     over_period.append(reference_dates[period]['name'])
    ##     investment_movements.append(df_summary_output.loc[df_summary_output['date_reference'] == period, 'Loans to households: Housing: Investment - movement'].values[0])
    ##     oo_movement.append(df_summary_output.loc[df_summary_output['date_reference'] == period, 'Loans to households: Housing: Owner-occupied - movement'].values[0])
    ## movements_table = pd.DataFrame({
    ##     "Period": over_period,
    ##     "Owner-Occupied Loans Increase": oo_movement,
    ##     "Investment Property Loans Increase": investment_movements,
    ## })
## 
    ## # Reset the index and drop it
    ## movements_table.reset_index(drop=True, inplace=True)
    ## summary_loans_dict['movements_table'] = movements_table
    ## 
## 
    ## # Period movements - monthly averages
    ## data = {
    ##     'Period': [
    ##         reference_dates['1_month']['name'],
    ##         reference_dates['6_months']['name'],
    ##         reference_dates['12_months']['name'],
    ##         reference_dates['long_term']['name'],
    ##     ],
    ##     'Investment loans movement': [
    ##         df_summary_1_month['Loans to households: Housing: Investment - movement'].values[0] / reference_dates['1_month']['months_int'],
    ##         df_summary_6_months['Loans to households: Housing: Investment - movement'].values[0] / reference_dates['6_months']['months_int'],
    ##         df_summary_12_months['Loans to households: Housing: Investment - movement'].values[0] / reference_dates['12_months']['months_int'],
    ##         df_summary_long_term['Loans to households: Housing: Investment - movement'].values[0] / reference_dates['long_term']['months_int'],
    ##     ],
    ##     'Owner-occupied loans movement': [
    ##         df_summary_1_month['Loans to households: Housing: Owner-occupied - movement'].values[0] / reference_dates['1_month']['months_int'],
    ##         df_summary_6_months['Loans to households: Housing: Owner-occupied - movement'].values[0] / reference_dates['6_months']['months_int'],
    ##         df_summary_12_months['Loans to households: Housing: Owner-occupied - movement'].values[0] / reference_dates['12_months']['months_int'],
    ##         df_summary_long_term['Loans to households: Housing: Owner-occupied - movement'].values[0] / reference_dates['long_term']['months_int'],
    ##     ],
    ## }
## 
    ## # Create the figure object
    ## fig = go.Figure()
## 
    ## # Add bars for investment data
    ## fig.add_trace(go.Bar(
    ##     x=data['Period'],
    ##     y=data['Investment loans movement'],
    ##     name='Investment loans movement',  # Legend entry
    ##     marker_color='#ff9999'  # Color of the bar
    ## ))
## 
    ## # Add bars for owner-occupied data
    ## fig.add_trace(go.Bar(
    ##     x=data['Period'],
    ##     y=data['Owner-occupied loans movement'],
    ##     name='Owner-occupied loans movement',
    ##     marker_color='#66b3ff'  # Color of the bar
    ## ))
## 
    ## # Update the layout for a grouped bar chart
    ## fig.update_layout(
    ##     title='Investment and Owner-occupied Property Loans - monthly averages',
    ##     xaxis_title='Period',
    ##     yaxis_title='Average Monthly Movement',
    ##     barmode='group',  # Group bars of different traces at each x value
    ##     xaxis_tickangle=-45,  # Rotate labels for better readability
    ##     legend=dict(
    ##         orientation="h",  # 'h' for horizontal (default is 'v' for vertical)
    ##         xanchor="center",  # Anchor point
    ##         x=0.5,  # Center the legend horizontally
    ##         y=-0.3  # Position the legend below the x-axis
    ##     )
    ## )
## 
    ## summary_housing_info['housing_movements_annualised'] = fig

    return summary_loans_dict
