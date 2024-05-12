import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

from calc_summary.summary_utils import determine_reference_dates
from calc_summary.summary_utils import column_pos_and_neg_movements_chart
from calc_summary.summary_utils import generate_pos_neg_charts
from calc_summary.summary_utils import generate_bar_chart
from utils import movement_text, dollar_movement_text, rounded_dollars


def generate_deposits_pos_neg_charts(
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

        loan_pos_neg_charts[f"deposits_pos_neg_chart_{reference_date}"] = column_pos_and_neg_movements_chart(
            df=df,
            category_column=category_column,
            prior_label=prior_label,
            movement_label=movement_label,
            title=f"Deposit Movements by Category - movements over {date_details['name']}",
            yaxis_title='Deposit Amount',
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


def generate_summary_deposits_dict(
        df_summary_output,
        date_column,
        selected_date,
        reference_dates,
):
    # Initiate summary charts and info dict 
    summary_deposits_dict = {}

    # List the deposits columns
    deposits_column_names = [
       'Deposits by non-financial businesses',
       'Deposits by financial institutions',
       'Deposits by general government',
       'Deposits by households',
       'Deposits by community service organisations',
       # 'Total residents deposits',
    ]

    # Generate bar chart for Deposits Totals
    summary_deposits_dict["deposit_totals_bar_chart"] = generate_bar_chart(
        df_summary_output=df_summary_output,
        selected_date=selected_date,
        column_names=deposits_column_names,
        category_column='Deposit Category',
        columns_label = 'Total Deposit Amount',
        marker_color='lightblue',
        title=f"Deposit Category Totals as at {selected_date.strftime('%d %B %Y')}",
        yaxis_title='Total Deposit Amount',
        margin_l=50,
        margin_r=200,
        margin_t=50,
        margin_b=180,
    )
    
    # Generate Deposit positive and negative movements charts
    summary_deposits_dict['deposit_pos_neg_charts'] = generate_pos_neg_charts(
        df_summary_output=df_summary_output,
        column_names=deposits_column_names,
        reference_dates=reference_dates,
        category_column='Deposit Category',
        grouping_name='Deposit',
    )

    return summary_deposits_dict
