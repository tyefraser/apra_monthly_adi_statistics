from yaml import safe_load, YAMLError


def read_yaml(file_path: str):
    try:
        with open(file_path, 'r') as file:
            yaml_data = safe_load(file)
        return yaml_data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except YAMLError as e:
        print(f"Error parsing YAML in '{file_path}': {e}")


def validate_single_column(
        complete_columns_list,
        column_variable,
        column_name,
):
    if not isinstance(column_name, str):
        raise ValueError(f"{column_variable} must be a string, not: {column_name}")
    
    if column_name not in complete_columns_list:
        raise ValueError(f"{column_variable} ({column_name}) must exist in the expected_columns_and_types_dict")
    

def validate_column_list(
        complete_columns_list,
        column_list_variable,
        column_name_list,
):
    if not isinstance(column_name_list, list):
        raise ValueError(f"{column_list_variable} must be a string, not: {column_name_list}")
    
    for i, column_name in enumerate(column_name_list):
        validate_single_column(
            complete_columns_list=complete_columns_list,
            column_variable=f"{column_list_variable} item-{i}",
            column_name=column_name,
        )


def validate_yamls(
        data_config_dict
):
    # Get the complete list of columns expected in df
    complete_columns_list = data_config_dict['expected_columns_and_types_dict'].keys()
    
    # Single column checks
    single_columns = {}
    single_columns['company_column'] = data_config_dict['column_settings']['company_column'] # 'Institution Name'
    for column_variable, column_name in single_columns.items():
        validate_single_column(
            complete_columns_list=complete_columns_list,
            column_variable=column_variable,
            column_name=column_name,
        )
    
    # Column lists
    column_lists = {}
    column_lists['dollars_conversion_all_but'] = data_config_dict['column_adjustments_dict']['dollars_conversion']['all_but']
    for column_list_variable, column_name_list in column_lists.items():
        validate_column_list(
            complete_columns_list=complete_columns_list,
            column_list_variable=column_list_variable,
            column_name_list=column_name_list,
        )


def read_yamls():
    # Get aliases from yaml
    aliases_dict = read_yaml(file_path = 'configs/aliases.yaml')

    # Set colour scheme
    color_discrete_map = read_yaml(file_path = 'configs/color_discrete_map.yaml')

    # Read data config
    data_config_dict = read_yaml(file_path = 'configs/data_config.yaml')

    # Initialize an empty dictionary for the transformed structure
    type_to_columns_dict = {}

    # Iterate over the original dictionary to populate the new structure
    for column, dtype in data_config_dict['expected_columns_and_types_dict'].items():
        if dtype not in type_to_columns_dict:
            type_to_columns_dict[dtype] = [column]
        else:
            type_to_columns_dict[dtype].append(column)
    data_config_dict['column_type_lists'] = type_to_columns_dict

    # Check if there is exactly one date column in the configuration
    if len(data_config_dict['column_type_lists']['date']) != 1:
        raise ValueError("There must only be 1 date column.")
    date_column = data_config_dict['column_type_lists']['date'][0] # 'Period'

    # outputs config
    outputs_config_dict = read_yaml(file_path = 'configs/outputs_config.yaml')

    # Validate yaml files
    validate_yamls(data_config_dict=data_config_dict)

    return aliases_dict, color_discrete_map, data_config_dict, date_column, outputs_config_dict
    