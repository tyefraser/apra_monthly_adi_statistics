import streamlit as st

from tabs.tab_utils import generate_tabs
from utils import dollar_movement_text

def generate_loans_tab(
        summary_dict,
        date_column,
        selected_date,
        entity_dict,
        data_config_dict,
):
    # Heading
    st.write("# Loan Accounts")
    st.write(
        f"As at **{selected_date.strftime('%d %B %Y')}** the market is made up of the following **loan accounts** "
        "(Please select the period to understand movements in the account over that timeframe): "
    )
    tab_1_month, tab_6_months, tab_12_months, tab_long_term, current_totals = st.tabs([
        "1 Month",
        "6 Months",
        "12 Months",
        "Long term",
        f"Totals as at {selected_date.strftime('%d %B %Y')}",
    ])
    with tab_1_month:
        st.plotly_chart(summary_dict['summary_loans_dict']['loan_pos_neg_charts']['loan_pos_neg_chart_1_month'], use_container_width=True)
    with tab_6_months:
        st.plotly_chart(summary_dict['summary_loans_dict']['loan_pos_neg_charts']['loan_pos_neg_chart_6_months'], use_container_width=True)
    with tab_12_months:
        st.plotly_chart(summary_dict['summary_loans_dict']['loan_pos_neg_charts']['loan_pos_neg_chart_12_months'], use_container_width=True)
    with tab_long_term:
        st.plotly_chart(summary_dict['summary_loans_dict']['loan_pos_neg_charts']['loan_pos_neg_chart_long_term'], use_container_width=True)
    with current_totals:
        st.plotly_chart(summary_dict['summary_loans_dict']["loan_totals_bar_chart"], use_container_width=True)


    # Housing Market
    st.write("## Housing Market")
    st.write(
        f"""
        The housing market is divided into owner-occupied and investment property loans.
        
        """
    )

    # Accounts
    st.write("## Housing Market Accounts")
    col_names = [
        'Total residents loans and finance leases',
        'Loans to non-financial businesses',
        'Loans to financial institutions',
        'Loans to general government',
        'Loans to households: Housing: Owner-occupied',
        'Loans to households: Housing: Investment',
        'Loans to households: Credit cards',
        'Loans to households: Other',
        'Loans to community service organisations',
    ]
    for col_name in col_names:
        st.write(f"### {col_name}")
        entity_col_dict = entity_dict[col_name]
        tab_dict = {}
        tab_dict["Current balances"] = [
            ['plot', entity_col_dict['balances_fig']],
        ]        
        keys = entity_col_dict.keys()
        for period_key in data_config_dict['reference_dates_config'].keys():
            period_movement_key = f"{period_key} - dollar movements fig"
            if period_movement_key in keys:
                tab_dict[period_key] = [
                    ['plot', entity_col_dict[period_movement_key]],
                ]
                # tab_dict[period_key] = st.plotly_chart(entity_col_dict[period_movement_key], use_container_width=True)
                # st.plotly_chart(summary_dict['summary_loans_dict']['loan_pos_neg_charts']['loan_pos_neg_chart_1_month'], use_container_width=True)
        generate_tabs(tab_dict=tab_dict)