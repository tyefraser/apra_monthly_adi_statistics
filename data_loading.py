import os
import pickle
import pandas as pd
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import quote
import requests

# from data_processing.business_loans.business_loans import business_loans_fn
from utils_dataframe_calcs import new_calculated_column

logger = logging.getLogger(__name__)

def load_url_xlsx():
    base_url = 'https://www.apra.gov.au/sites/default/files/'
    last_month_eom = datetime.now().replace(day=1) - timedelta(days=1)
    last_month_yyyy_mm = last_month_eom.strftime('%Y-%m')
    file_path = '/Monthly%20authorised%20deposit-taking%20institution%20statistics%20back-series%20March%202019%20-%20'
    two_months_ago = last_month_eom - relativedelta(months=1)
    two_months_ago_mmm_yyyy = two_months_ago.strftime('%B %Y')
    file_extension = '.xlsx'

    # Concatenate the strings to form the full URL
    full_url = base_url + last_month_yyyy_mm + file_path + quote(two_months_ago_mmm_yyyy) + file_extension

    try:
        # Set xlsx path
        file_name = f"data/madis_{two_months_ago_mmm_yyyy}.xlsx".replace(' ', '_')

        if os.path.exists(file_name):
            logger.info(f"Excel file has already been downloaded.")
        else:
            # Attempt to load URL xlsx
            response = requests.get(full_url)
            response.raise_for_status()  # This will raise an exception if there is an error

            with open(file_name, 'wb') as f:
                f.write(response.content)

            logger.debug(f"File downloaded successfully! file_name:{file_name}")
    except Exception as e:
        logger.info(f"Failed to download the file: {e}")

        # Set xlsx path
        file_name = 'data_historical/Monthly authorised deposit-taking institution statistics back-series March 2019 - December 2023.xlsx'
        logger.info(f"Using alternative file: {file_name}")
    
    return file_name


def check_column_coverage(df, drop_cols_list, numeric_cols):
    """
    Checks if drop_cols_list and numeric_cols cover all columns in df.
    
    Parameters:
    - df (pandas.DataFrame): DataFrame to check.
    - drop_cols_list (list): List of columns to drop.
    - numeric_cols (pandas.Index): Index object of numeric columns.
    """
    all_cols_set = set(df.columns)
    combined_set = set(drop_cols_list).union(set(numeric_cols))
    
    if combined_set != all_cols_set:
        not_covered_cols = all_cols_set - combined_set
        logger.warning(f"Columns not covered by drop or numeric lists: {not_covered_cols}")


def convert_columns_by_type(df, cols_list, cols_type):
    """
    Convert specified columns in a DataFrame to the specified data type.

    Parameters:
        df (pd.DataFrame): The DataFrame to perform column conversions on.
        cols_list (list): List of column names to convert.
        cols_type (str): Desired data type for the specified columns ('date', 'str', 'float').

    Raises:
        ValueError: If an unexpected data type is provided.

    Returns:
        None: The function modifies the DataFrame in place.
    """
    if cols_type == 'date':
        df[cols_list] = df[cols_list].apply(pd.to_datetime, errors='coerce').apply(lambda x: x.dt.date)
    elif cols_type == 'str':
        df[cols_list] = df[cols_list].astype(str)
    elif cols_type == 'float':
        df[cols_list] = df[cols_list].astype(float)
    else:
        raise ValueError('Unexpected data type. Supported types are: "date", "str", "float".')
    
    return df


def convert_columns_dict_type_allocation(df, col_types_dict):
    # Initialize an empty dictionary for the transformed structure
    type_to_columns_dict = {}

    # Iterate over the original dictionary to populate the new structure
    for column, dtype in col_types_dict.items():
        if dtype not in type_to_columns_dict:
            type_to_columns_dict[dtype] = [column]
        else:
            type_to_columns_dict[dtype].append(column)
    
    for column_type, column_list in type_to_columns_dict.items():
        df = convert_columns_by_type(
                df=df,
                cols_list=column_list,
                cols_type=column_type
            )

    return df


def column_scaling(df, col_list, adjustment_type, adjustment_value):
    """
    Scale specified columns in a DataFrame based on the provided adjustment type and value.

    Parameters:
        df (pandas.DataFrame): The DataFrame to be scaled.
        col_list (list): A list of column names to be scaled.
        adjustment_type (str): The type of adjustment to be applied ('multiply' for multiplication).
        adjustment_value (float): The value by which the columns will be adjusted.

    Returns:
        pandas.DataFrame: The DataFrame with scaled columns.
    """
    if adjustment_type == 'multiply':
        df[col_list] *= adjustment_value
    return df

def column_adjustments(df, config_dict):
    """
    Apply specified column adjustments to a DataFrame based on the provided configuration dictionary.

    Parameters:
        df (pandas.DataFrame): The DataFrame to which adjustments will be applied.
        config_dict (dict): A dictionary containing adjustment details.

    Returns:
        pandas.DataFrame: The DataFrame with applied adjustments.
    """
    if 'column_adjustments_dict' in config_dict:
        adjustments_dict = config_dict['column_adjustments_dict']

        for _, adj_details in adjustments_dict.items():
            if 'all_but' in adj_details:
                col_list = df.columns[~df.columns.isin(adj_details['all_but'])]
            elif 'all_of' in adj_details:
                col_list = adj_details['all_of']
            else:
                raise ValueError("Error: only accept values of 'all_but' or 'all_of'")

            for adj_type, adj_value in adj_details['ordered_adjustments'].items():
                df = column_scaling(df, col_list, adjustment_type=adj_type, adjustment_value=adj_value)

    return df


def generate_calculated_columns(
        df,
        calculated_columns_dict,
):
    for new_column_name, calculations in calculated_columns_dict.items():
        df[new_column_name] = 0
        for column_calculation in calculations:
            calculation = column_calculation[0]
            column = column_calculation[1]
            df = new_calculated_column(
                df=df,
                new_column_name=new_column_name,
                calculation=calculation,
                column=column,
            )
    
    return df


def read_and_process_data(
        file_name,
        data_config_dict,
        date_column,
):
    """
    Reads and processes data from an Excel file according to specified configurations.

    Parameters:
    - file_name (str): The path to the Excel file to be read.
    - data_config_dict (dict): A dictionary containing data configuration details such as:
        - file_loading_details: Dict with keys 'sheet_name' and 'skiprows' for loading the file.
        - expected_columns_list: List of expected columns in the file.
        - column_typing_dict: Dict specifying the data types for columns.
    - date_column (str): The name of the column containing dates to be processed as datetime objects.

    Returns:
    - pandas.DataFrame: The processed DataFrame.
    """
    try:
        # Load the Excel file
        df = pd.read_excel(
            io=file_name,
            sheet_name=data_config_dict['file_loading_details']['sheet_name'],
            skiprows=data_config_dict['file_loading_details']['skiprows'],
        )
        logger.info("Excel data loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load Excel file data: {e}")
        raise

    # Ensure the expected columns exist
    expected_columns = set(data_config_dict['expected_columns_and_types_dict'].keys())
    if not expected_columns.issubset(df.columns):
        missing_columns = expected_columns - set(df.columns)
        logger.error(f"Missing expected columns: {missing_columns}")
        raise ValueError(f"Missing expected columns: {missing_columns}")
    
    # Identify columns in the DataFrame that are not in the expected columns list
    unexpected_columns = set(df.columns) - expected_columns
    if unexpected_columns:
        logger.info(f"Dropping unexpected columns: {unexpected_columns}")
        df = df.drop(columns=unexpected_columns)

    # Column Data Types
    df=convert_columns_dict_type_allocation(
        df=df.copy(),
        col_types_dict=data_config_dict['expected_columns_and_types_dict'],
    )
    
    # Processing steps
    df.sort_values(by=date_column, inplace=True)
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

    # Identify columns for processing
    drop_cols_list = [date_column] + data_config_dict['column_type_lists']['str']
    numeric_cols = df.select_dtypes(include=['float64']).columns.difference(drop_cols_list)
    
    # Integrity checks
    check_column_coverage(df, drop_cols_list, numeric_cols)

    # Clean data
    df.dropna(subset=drop_cols_list, inplace=True)
    df = df.drop_duplicates(subset=drop_cols_list, keep='first')
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Column Adjustments - convert to dollar amounts (not scaled)
    df=column_adjustments(df, data_config_dict)

    # Create calculated columns
    df = generate_calculated_columns(
        df=df,
        calculated_columns_dict=data_config_dict['source_data_calculated_columns'],
    )

    return df


def generate_summary(
        df,
        date_column,
        data_config_dict,
):
    # Create summary dataframe from copy of df
    df_summary = df.copy()

    # Drop the string columns as they are not needed for the pivot
    df_summary.drop(columns=data_config_dict['column_type_lists']['str'], inplace=True)

    # Group by the extracted year and month, then sum up all numeric columns for each group
    df_summary = df_summary.groupby([date_column]).sum().reset_index()

    df_summary = generate_calculated_columns(
        df=df_summary,
        calculated_columns_dict=data_config_dict['summary_data_calculated_columns']
    )

    return df_summary


def fill_company_data_for_all_dates(
        df_cleaned,
        date_column,
        company_column,
):
    """
    Ensures every company has data all dates
    """

    # Create a date range covering all months in your data
    date_range = pd.date_range(start=df_cleaned[date_column].min(), end=df_cleaned[date_column].max(), freq='M')

    # Create a DataFrame of all unique companies and all months
    all_companies = df_cleaned[company_column].unique()
    all_periods = pd.DataFrame(date_range, columns=[date_column])
    all_periods['key'] = 1
    all_companies_df = pd.DataFrame(all_companies, columns=[company_column])
    all_companies_df['key'] = 1

    # Cartesian product of companies and periods
    complete_df = pd.merge(all_periods, all_companies_df, on='key')[[date_column, company_column]].copy()
    complete_df = complete_df[[date_column, company_column]].copy()

    # Merge with the original DataFrame
    final_df = pd.merge(complete_df, df_cleaned, on=[date_column, company_column], how='left')
    final_df

    # Replace NaNs with zeros
    final_df.fillna(0, inplace=True)

    return final_df

def rank_companies(df, date_column, value_cols):
    """
    Ranks companies within each month for specified value columns.
    
    Parameters:
    - df: DataFrame containing the data.
    - date_column: Column name with datetime representing the month.
    - value_cols: List of column names with dollar amounts to rank.
    
    Returns:
    - DataFrame with ranks added for each value column.
    """
    # Ensure the date column is in datetime format
    # df[date_column] = pd.to_datetime(df[date_column]).dt.to_period('M')
    
    # Function to rank companies within each group
    def rank_within_group(group, cols):
        for col in cols:
            rank_col_name = f"{col} - Rank"
            group[rank_col_name] = group[col].rank(method='dense', ascending=False).astype('int')
        return group
    
    # Apply the ranking function for each month and value column
    ranked_df = df.groupby(date_column, group_keys=False).apply(rank_within_group, value_cols)
    
    return ranked_df


def generate_cleaned_df( ## To DO: Cal this "clean" rather than "original" and update source to original
        df,
        date_column,
        data_config_dict,
):
    # Initiate dataframe
    df_cleaned = df.copy()

    # Get company and abn column names
    company_column = data_config_dict['column_settings']['company_column']
    abn_column = data_config_dict['column_settings']['abn_column']

    # First, find all unique companies that have duplicates in any given month
    duplicate_companies = df_cleaned[df_cleaned.duplicated([date_column, company_column], keep=False)][company_column].unique()

    # Append ABN to these company names globally across all their occurrences
    for company in duplicate_companies:
        df_cleaned.loc[df_cleaned[company_column] == company, company_column] = df_cleaned[company_column] + ' (' + df[abn_column] + ')'

    # Remove excluded columns
    df_cleaned = df_cleaned.drop(columns=[abn_column])

    # Ensure every company has data completed within each row
    df_cleaned = fill_company_data_for_all_dates(
        df_cleaned=df_cleaned,
        date_column=date_column,
        company_column=company_column,
    )

    # Generate ranking columns
    group_by_columns = (
        data_config_dict['column_type_lists']['str'] + data_config_dict['column_type_lists']['date']
    )
    ranking_columns = list(set(df_cleaned.columns) - set(group_by_columns))
    df_cleaned = rank_companies(
        df=df_cleaned,
        date_column=date_column,
        value_cols=ranking_columns,
    )
    # for col in ranking_columns:
    #     rank_col_name = f"{col} - rank"
    #     # Adjust ranking method here. Using 'average' (default) or 'first'.
    #     df_cleaned[rank_col_name] = df_cleaned.groupby(date_column)[col].rank(method="first").astype('int')

    return df_cleaned

def data_loader(
        pkl_folder_name,
        data_config_dict,
        date_column,
):
    logger.info("Executing: data_loader")

    # Set pickle variable paths
    df_original_pkl=os.path.join(pkl_folder_name, "df_original.pkl")
    df_cleaned_pkl=os.path.join(pkl_folder_name, "df_cleaned.pkl")
    df_summary_pkl=os.path.join(pkl_folder_name, "df_summary.pkl")

    # Check if data has already been loaded into pkl file
    if os.path.exists(df_cleaned_pkl) and os.path.exists(df_summary_pkl):
        # Data exists, load it from pickle
        logger.info("Loading data from pickle files")

        # Load df original data
        with open(df_original_pkl, 'rb') as f:
            df_original = pickle.load(f)

        # Load df cleaned data
        with open(df_cleaned_pkl, 'rb') as f:
            df_cleaned = pickle.load(f)
        
        # Load df summary data
        with open(df_summary_pkl, 'rb') as f:
            df_summary = pickle.load(f)

    else:
        # Data needs to be sourced from APRA website
        logger.info("Loading data from APRA website")

        # Load data
        original_file_name=load_url_xlsx()

        # Read and process data
        df_original = read_and_process_data(
            data_config_dict=data_config_dict,
            file_name=original_file_name,
            date_column=date_column,
        )
        
        # Generate summary data frame
        df_summary = generate_summary(
                df=df_original,
                date_column=date_column,
                data_config_dict=data_config_dict,
        )

        # Generate original data frame
        df_cleaned = generate_cleaned_df(
            df=df_original,
            date_column=date_column,
            data_config_dict=data_config_dict,
        )

        # Write data frame to pickle file
        with open(df_original_pkl, 'wb') as f:
            pickle.dump(df_original, f)

        with open(df_cleaned_pkl, 'wb') as f:
            pickle.dump(df_cleaned, f)

        # Write summary data frame to pickle file
        with open(df_summary_pkl, 'wb') as f:
            pickle.dump(df_summary, f)

    logger.info("Executed: data_loader")
    return df_original, df_cleaned, df_summary
