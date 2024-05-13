import streamlit as st

from tabs.tab_utils import generate_tabs


def generate_other_tab(
        summary_dict,
        date_column,
        selected_date,
        entity_dict,
        data_config_dict,
):
    # Heading
    st.write("# Other Accounts")
    
    col_names = [
        'Cash and deposits with financial institutions',
        'Trading securities',
        'Investment securities',
        'Total residents assets',
        'Total securitised assets on balance sheet',
        'Intra-group loans and finance leases',
        'Intra-group deposits',
        'Negotiable Certificates of Deposit',
        'Total short-term borrowings',
        'Total long-term borrowings',
        # 'Business Loans',
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