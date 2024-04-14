import streamlit as st

from utils import dollar_movement_text

def generate_market_overview_tab(
        summary_dict,
        date_column,
        selected_date,
):

    # Allocate variables
    df_summary_output=summary_dict['df_summary_output']
    reference_dates=summary_dict['reference_dates']
    df_summary_1_month = df_summary_output[
        df_summary_output[date_column] == reference_dates['1_month']['date']]

    # Generate tab
    st.write("# Market Overview")

    # Housing Market
    st.write("## Housing Market")
    st.write(
        f"""
        The housing market is divided into owner-occupied and investment property loans.
        As at {selected_date.strftime('%d %B %Y')} the market is divided as follows:
        """
    )
    
    st.plotly_chart(summary_dict['summary_housing_info']['housing_percentages_pie'])

    ## st.write("### Housing - Period Movements")
    ## st.write(
    ##     f"""
    ##     - {summary_dict['summary_housing_info']['housing_oo_i_movements_1_month']}
    ##     - {summary_dict['summary_housing_info']['housing_oo_i_movements_6_months']}
    ##     - {summary_dict['summary_housing_info']['housing_oo_i_movements_12_months']}
    ##     - {summary_dict['summary_housing_info']['housing_oo_i_movements_long_term']}
    ##     """
    ## )

    # Custom CSS to inject into the Streamlit interface for right alignment
    st.markdown("""
    <style>
    div[data-testid="stBlock"] .dataframe-container .table td,
    div[data-testid="stBlock"] .dataframe-container .table th {
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

    # Display the DataFrame with right-aligned data
    st.write("Movement across periods:")
    st.dataframe(summary_dict['summary_housing_info']['movements_table'], use_container_width=True, hide_index=True)
    


    ## st.write(
    ##     """
    ##     The following graph contains the investment and owner-occupied movements as a monthly average for comparability:
    ##     """
    ## )
    st.plotly_chart(summary_dict['summary_housing_info']['housing_movements_annualised'])
    
