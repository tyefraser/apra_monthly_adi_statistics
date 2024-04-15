import streamlit as st

from utils import dollar_movement_text

def generate_deposits_tab(
        summary_dict,
        date_column,
        selected_date,
):
    # Heading
    st.write("# Deposit Accounts")
    st.write(
        f"As at **{selected_date.strftime('%d %B %Y')}** the market is made up of the following **deposit accounts** "
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
        st.plotly_chart(summary_dict['summary_deposits_dict']['deposit_pos_neg_charts']['deposit_pos_neg_chart_1_month'], use_container_width=True)
    with tab_6_months:
        st.plotly_chart(summary_dict['summary_deposits_dict']['deposit_pos_neg_charts']['deposit_pos_neg_chart_6_months'], use_container_width=True)
    with tab_12_months:
        st.plotly_chart(summary_dict['summary_deposits_dict']['deposit_pos_neg_charts']['deposit_pos_neg_chart_12_months'], use_container_width=True)
    with tab_long_term:
        st.plotly_chart(summary_dict['summary_deposits_dict']['deposit_pos_neg_charts']['deposit_pos_neg_chart_long_term'], use_container_width=True)
    with current_totals:
        summary_dict
        # st.plotly_chart(summary_dict['summary_deposits_dict']["deposit_totals_bar_chart"], use_container_width=True)

