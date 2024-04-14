
from math import floor, log10
from dateutil.relativedelta import relativedelta

import os
from pathlib import Path
import logging
import logging.config
import yaml
from math import isnan

def project_absolute_path() -> Path:
    return Path(__file__).resolve().parents[0]

def absolute_path(dir: str) -> str:
    return os.path.join(project_absolute_path(), dir)


def setup_logging(default_path='logging_config.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging configuration
    """
    path = absolute_path(dir=default_path)
    
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        logging.info('Running yaml logger')
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.info('Running default logger, not from the yaml')
        logging.basicConfig(level=default_level)

# Set up logging using the configuration file
# setup_logging()

# Create a logger variable
logger = logging.getLogger(__name__)

def create_directory_if_not_exists(absolute_path):
    # Extract the directory path
    directory_path = os.path.dirname(absolute_path)

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def assert_file_extension(
        file_name,
        expected_extension: str = '.xlsx',
):
    logger.debug('\n\n\nRunning: assert_file_extension')

    file_extension=os.path.splitext(file_name)[1]
    try:
        assert (file_extension == expected_extension), (
            f"Incorrect file extension, expecting '{expected_extension}' but got '{file_extension}'"
        )
        return True        
    except AssertionError as e:
        logger.info(f"AssertionError: {e}")
        raise AssertionError(f"AssertionError: {e}")


def rounded_number(number):
    if (number is None) or (isnan(number)):
        formatted_amount = None
    else:
        scales = ['', 'K', 'M', 'Bn', 'Trn', 'Quadr', 'Quint', 'Sext', 'Sept', 'Oct', 'Non', 'Dec']  # Suffixes for scaling
        
        # Determine the appropriate scale
        scale_index = 0
        number_rounded = number
        while abs(number_rounded) >= 1000 and scale_index < len(scales) - 1:
            number_rounded /= 1000
            scale_index += 1
        
        # Check number is within accepted scale
        if scale_index >= len(scales):
            raise ValueError("Absolute value of amount is too big to handle")  # Raise ValueError if scale index exceeds available scales
        
        # Adjust check for negative numbers
        sign = ''
        if number_rounded < 0:
            sign = '-'
            number_rounded = -1 * number_rounded

        # Format string
        number_string = "{:.2f}".format(number_rounded)
        number_string_len=len(number_string)

        # Round to appropriate decimal places based on integer part of the number
        if number_string_len == 4:
            formatted_amount = f"{number_string}"
        elif number_string_len == 5:
            formatted_amount = f"{number_string[0:4]}"
        elif number_string_len == 6:
            formatted_amount = f"{number_string[0:3]}"
        elif number_string_len == 7:
            formatted_amount = f"{number_string[0:4]}"
        else:
            # raise ValueError("Something went wrong")
            print('error')
            print(number)
            print(number_rounded)
            print(number_string)
            print(number_string_len)
            print(scale_index)

    logger.info(formatted_amount)
    return sign, formatted_amount, scales[scale_index]

def rounded_dollars(dollars):
    sign, dollars, scale = rounded_number(number = dollars)
    return f'{sign}$ {dollars} {scale}'

def rounded_dollars_md(dollars):
    sign, dollars, scale = rounded_number(number = dollars)
    return f'{sign}\\$&nbsp;{dollars}&nbsp;{scale}'


def dollar_movement_text(
          dollar_movement
):
    if dollar_movement > 0:
        txt = f'increased by {rounded_dollars_md(dollar_movement)}'
    elif dollar_movement < 0:
        txt = f'decreased by {rounded_dollars_md(dollar_movement)}'
    else:
        txt = 'remained unchanged'
    
    return txt

def movement_text(
          movement
):
    if movement > 0:
        txt = f'increased'
    elif movement < 0:
        txt = f'decreased'
    else:
        txt = 'remained unchanged'
    
    return txt





def escape_dollar_signs(text):
    # Escaping all dollar signs for Markdown and avoiding HTML entities
    return text.replace("$", "\\$").replace("\\\\$", "\\$")

def movement_values(
    start: float,
    end: float,
):
    # Movement variables
    movement = (end - start)
    movement_perc = movement/start

    return movement, movement_perc

def percentage_to_string(percentage):
    if percentage == 0:
        return "0%"
    
    # Calculate the magnitude as the number of digits before the decimal point
    magnitude = floor(-log10(percentage))
    
    # Adjust precision based on the magnitude
    # Ensure a minimum of 1 digit and a maximum of 5 digits after the decimal
    precision = min(max(magnitude, 1), 5)
    
    # Format the percentage string with dynamic precision
    percentage_str = f"{percentage * 100:.{precision}f}%"
    
    return percentage_str

def ranking_position(rank):
    # Get last digiti in rank number
    last_digit = rank % 10
    last_2_digits = rank % 100
    rank_str = str(int(rank))

    # Get position wording
    if last_digit == 1 and (last_2_digits != 11):
        position = rank_str + 'st'
    elif last_digit == 2 and (last_2_digits != 12):
        position = rank_str + 'nd'
    elif last_digit == 3 and (last_2_digits != 13):
        position = rank_str + 'rd'
    else:
        position = rank_str + 'th'
    
    return position

def period_ago(months_ago):
    if months_ago == 0:
        period_txt = 'current month'
    elif (months_ago % 12) == 0:
        yrs = months_ago / 12
        if yrs == 1:
            period_txt = 'year'
        else:
            period_txt = f"{int(yrs)} years"
    else:
        if months_ago == 1:
            period_txt = 'month'
        else:
            period_txt = f"{int(months_ago)} months"
    return period_txt

def period_ago_prefix(months_ago):
    if months_ago == 0:
        prefix_txt = 'current month'
    elif months_ago == 1:
        prefix_txt = 'MoM'
    elif (months_ago / 12) == 1:
        prefix_txt = 'YoY'
    elif (months_ago % 12) == 0:
        yrs = months_ago / 12
        prefix_txt = f"{int(yrs)} years"
    else:
        prefix_txt = f"{int(months_ago)} months"
    return prefix_txt

def position_s_movement(position_movement):
    if position_movement == 1:
        text = 'position'
    else:
        text = 'positions'
    return text

