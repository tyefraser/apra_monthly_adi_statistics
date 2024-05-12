import logging
import os
import pickle
import pandas as pd
import numpy as np

from chart_generator import chart_selected_col_bar
from utils import rounded_dollars, format_percentage


logger = logging.getLogger(__name__)


def initiate_col_to_graph_current_df(
        col_to_graph_df,
        date_column,
        selected_date,
        company_column,
        col_to_graph,
        company_order_list,
        color_discrete_map,
):
    col_to_graph_current_df = col_to_graph_df[
            col_to_graph_df[date_column] == selected_date].copy()

    # Set monthly total value
    month_total_column = f"{col_to_graph} - month total"
    total_sum = col_to_graph_current_df[col_to_graph].sum() 
    col_to_graph_current_df[month_total_column] = total_sum

    # Percentage of market - assumes market total isn't zero
    month_market_perc = f"{col_to_graph} - market percentage"
    col_to_graph_current_df[month_market_perc] = (
        col_to_graph_current_df[col_to_graph] / col_to_graph_current_df[month_total_column]
    )

    # Balance chart text
    text_column = f"{col_to_graph} - text"
    formatted_dollars  = col_to_graph_current_df[col_to_graph].apply(rounded_dollars)
    formatted_percentages = col_to_graph_current_df[
        f"{col_to_graph} - market percentage"].apply(lambda x: f"(share: {x * 100:.1f} %)")
    text_column = f"{col_to_graph} - text"
    col_to_graph_current_df[text_column] = formatted_dollars + ' ' + formatted_percentages

    col_fig = chart_selected_col_bar(
            df=col_to_graph_current_df.copy(),
            category_column=company_column,
            reference_col=col_to_graph,
            title = f"{selected_date.strftime('%d %B %Y')} Month End Balances",
            ordered_category_list=company_order_list,
            show_xaxis_labels = True,
            x_tickformat = None,
            x_gridcolor = 'Grey',
            color_discrete_map=color_discrete_map,
    )

    return col_to_graph_current_df, col_fig


def period_movements(
        col_to_graph_df,
        col_to_graph_current_df,
        col_to_graph,
        date_column,
        selected_date,
        company_column,
        data_config_dict,
        company_order_list,
        color_discrete_map,
):
    # initiate dictionary
    period_movements_dict = {}

    # Run through all month in the reference_dates_config
    for period_key, period_values in data_config_dict['reference_dates_config'].items():
        # Calculate the month end date of the reference month based on months_int
        date_value = (
            pd.to_datetime(selected_date).date() - 
            pd.DateOffset(months=period_values['info']['months_int'])
        ) + pd.offsets.MonthEnd(0)

        # Check if date_value exists in the date_column
        if date_value in col_to_graph_df[date_column].values:
            reference_balance_col = f"{col_to_graph} - {period_key} - balance"
            ref_bal_mvmt_dol_col = f"{col_to_graph} - {period_key} - movement ($)"
            ref_bal_mvmt_dol_col_txt = f"{col_to_graph} - {period_key} - movement ($) - text"
            ref_bal_mvmt_perc_col = f"{col_to_graph} - {period_key} - CAGR (%)"
            ref_bal_mvmt_perc_col_txt = f"{col_to_graph} - {period_key} - CAGR (%) - text"

            # Merge the reference data data to the current df
            filtered_df = col_to_graph_df[
                col_to_graph_df[date_column] == date_value][[company_column, col_to_graph]].copy()
            filtered_df.rename(columns={col_to_graph: reference_balance_col}, inplace=True)
            col_to_graph_current_df = col_to_graph_current_df.merge(
                filtered_df,
                on=company_column,
                how='left',
            )

            # Create the dollar movement column
            col_to_graph_current_df[ref_bal_mvmt_dol_col] = (
                col_to_graph_current_df[col_to_graph] -
                col_to_graph_current_df[reference_balance_col]
            )

            # Create the percentage movement column with proper zero handling
            col_to_graph_current_df[ref_bal_mvmt_perc_col] = np.where(
                col_to_graph_current_df[reference_balance_col] != 0,
                ((1 + (
                    col_to_graph_current_df[ref_bal_mvmt_dol_col] /
                    col_to_graph_current_df[reference_balance_col]
                )) ** (12 / period_values['info']['months_int'])) - 1,
                np.nan
            )

            # Movement text
            formatted_dollars  = col_to_graph_current_df[
                ref_bal_mvmt_dol_col].apply(rounded_dollars)
            formatted_percentages = col_to_graph_current_df[
                ref_bal_mvmt_perc_col].apply(lambda x: f"{x * 100:.1f}")
            col_to_graph_current_df[ref_bal_mvmt_dol_col_txt] = (
                    formatted_dollars + ' (CAGR: ' + formatted_percentages +  "%)"
            )
            col_to_graph_current_df[ref_bal_mvmt_perc_col_txt] = (
                formatted_percentages +  "% CAGR (" + formatted_dollars + ')'
            )

            # Graph dollar movements
            period_movements_dict[f"{period_key} - dollar movements fig"] = chart_selected_col_bar(
                df=col_to_graph_current_df.copy(),
                category_column=company_column,
                reference_col=ref_bal_mvmt_dol_col,
                title = f"Dollar movements as at {selected_date.strftime('%d %B %Y')}",
                ordered_category_list=company_order_list,
                show_xaxis_labels = True,
                x_tickformat = None,
                x_gridcolor = 'Grey',
                color_discrete_map=color_discrete_map,
                xaxis_title=f"Dollar movements {period_values['info']['over_period'].lower()}"
            )

            # Graph percentage movements
            period_movements_dict[f"{period_key} - CAGR movements fig"] = chart_selected_col_bar(
                df=col_to_graph_current_df.copy(),
                category_column=company_column,
                reference_col=ref_bal_mvmt_perc_col,
                title = f"Dollar movements as at {selected_date.strftime('%d %B %Y')}",
                ordered_category_list=company_order_list,
                show_xaxis_labels = True,
                x_tickformat = None,
                x_gridcolor = 'Grey',
                color_discrete_map=color_discrete_map,
                xaxis_title=f"CAGR over {period_values['info']['name']}"
            )

        else:
            logger.debug(f"{date_value} doesn't exist in the data, no graph created")
    
    return col_to_graph_current_df, period_movements_dict


def graph_columns(
        df_cleaned,
        date_column,
        selected_date,
        company_column,
        selected_company,
        top_x_value,
        value_columns_to_graph_list,
        color_discrete_map,
        data_config_dict,
        other_col = 'Other',
):
    # Initiate dictionary
    graphed_columns_dict = {}

    for col_to_graph in value_columns_to_graph_list:
        logger.info(f"col: {col_to_graph}")
        # Initiate dict
        col_dict = {}

        # Get top_x company order for consistency across graphs
        df_cleaned_ordered = df_cleaned[
            (df_cleaned[date_column] == selected_date)
        ][[date_column, company_column, col_to_graph]].copy()
        top_x_companies = list(df_cleaned_ordered.sort_values(
            by=col_to_graph, ascending=False).head(top_x_value)[company_column])
        del df_cleaned_ordered
        if selected_company not in top_x_companies:
            top_x_companies.pop()
            top_x_companies.append(selected_company)

        # Filter DataFrame to get rows for top companies only
        top_companies_df = df_cleaned[
            df_cleaned[company_column].isin(top_x_companies)
        ][[date_column, company_column, col_to_graph]].copy()

        # Filter DataFrame for 'other' companies and group by date_column to sum their values
        other_companies_df = df_cleaned[
            ~df_cleaned[company_column].isin(top_x_companies)][[date_column, col_to_graph]]
        other_companies_grouped = other_companies_df.groupby(date_column).sum().reset_index()
        other_companies_grouped[company_column] = other_col

        # Combine top companies data with 'Other' companies data
        col_to_graph_df = pd.concat([top_companies_df, other_companies_grouped])
        
        # reset index
        col_to_graph_df.reset_index(drop=True, inplace=True)

        # Ordered company list
        company_order_list = top_x_companies
        company_order_list.append(other_col)

        col_to_graph_current_df, col_fig = initiate_col_to_graph_current_df(
            col_to_graph_df=col_to_graph_df,
            date_column=date_column,
            selected_date=selected_date,
            company_column=company_column,
            col_to_graph=col_to_graph,
            company_order_list=company_order_list,
            color_discrete_map=color_discrete_map,
        )

        # Calculate Period Movements
        col_to_graph_current_df, period_movements_dict = period_movements(
            col_to_graph_df=col_to_graph_df,
            col_to_graph_current_df=col_to_graph_current_df,
            col_to_graph=col_to_graph,
            date_column=date_column,
            selected_date=selected_date,
            company_column=company_column,
            data_config_dict=data_config_dict,
            company_order_list=company_order_list,
            color_discrete_map=color_discrete_map,
        )
    
        # Update column dictionary
        col_dict['df'] = col_to_graph_current_df
        col_dict['balances_fig'] = col_fig
        col_dict.update(period_movements_dict)

        # Update graphed columns dictionary
        graphed_columns_dict[col_to_graph] = col_dict

    return graphed_columns_dict


def generate_entity_outputs(
        df_cleaned,
        date_column,
        selected_date,
        company_column,
        selected_company,
        top_x_value,
        pkl_folder_name,
        data_config_dict,
        color_discrete_map,
):
    logger.info("Executing: generate_entity_outputs")

    # Set pickle variable path
    entity_dict_pkl=os.path.join(
        pkl_folder_name,
        f"entity_pickle-{selected_date.strftime('%Y-%m-%d')}_{top_x_value}.pkl"
    )

    # Check if entity data already exists and load it, otherwise create the empty dictionary
    if os.path.exists(entity_dict_pkl):
        # Data exists, load it from pickle
        logger.info("Loading entity data from pickle files")

        # Load df original data
        with open(entity_dict_pkl, 'rb') as f:
            entity_dict = pickle.load(f)

    else:
        logger.info("Creating empty entity dictionary")

        entity_dict = {}

    # Filter selections key
    entity_key = f"{selected_date.strftime('%Y-%m-%d')}_{selected_company}_top_{top_x_value}"

    if entity_key in entity_dict.keys():
        # Values already calculated, do nothing
        logger.info("Entity calculations have already been performed")
    else:
        # Perform calcs for entity
        logger.info("Performing entity calculations")

        # create entity outputs
        entity_dict[entity_key] = graph_columns(
            df_cleaned=df_cleaned,
            date_column=date_column,
            selected_date=selected_date,
            company_column=company_column,
            selected_company=selected_company,
            top_x_value=top_x_value,
            value_columns_to_graph_list=data_config_dict['value_columns_to_graph'].keys(),
            color_discrete_map=color_discrete_map,
            data_config_dict=data_config_dict,
            other_col = 'Other',
        )

        # Write entity dictionary to pickle file
        with open(entity_dict_pkl, 'wb') as f:
            pickle.dump(entity_dict, f)

    return entity_dict[entity_key]