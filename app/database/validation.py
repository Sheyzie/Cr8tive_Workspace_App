from utils.general import is_valid_date, matches_regex

'''
This model holds all the field level validation
'''

GENERAL_VALIDATION = {
    'is_none': lambda value, arg=None: value is None
}


VALIDATOR_MAP = {
    'str': {
        'name': 'String Validation',
        'validators': {
            **GENERAL_VALIDATION,
            'is_digit': lambda value, exp_value: isinstance(value, str) and value.isdigit(),
            'is_alpha': lambda value, exp_value: isinstance(value, str) and value.isalpha(),
            'is_alpha_num': lambda value, exp_value: isinstance(value, str) and value.isalnum(),
            'max_characters': lambda value, max: not len(value) >= max,
            'min_characters': lambda value, min: not len(value) < min,
            'character_length': lambda value, length: not len(value) == length,
            'is_value': lambda value, exp_value: value == exp_value,
            'is_present': lambda value, values_list: value in values_list,
            'full_pattern_match': lambda value, pattern: matches_regex(value, pattern),
            'partial_pattern_match': lambda value, pattern: matches_regex(value, pattern, partial=True),
        }
    },
    'int': {
        'name': 'Number Validation',
        'validators': {
            **GENERAL_VALIDATION,
            'is_greater': lambda value, num: value > num,
            'is_lesser': lambda value, num: value < num,
            'is_equal': lambda value, num: value == num,
            'is_present': lambda value, values_list: value in values_list,
        }
    },
    'datetime': {
        'name': 'Date Validation',
        'validators': {
            **GENERAL_VALIDATION,
            'is_valid_date': lambda date_string, date_format: is_valid_date(date_string=date_string, date_format=date_format)
        }
    },
    'bool': {
        'name': 'Bool Validation',
        'validators': {
            **GENERAL_VALIDATION,
            'is_true': lambda value, bool: value is True,
            'is_false': lambda value, bool: value is False,
        },
    },
    'UUID': {
        'name': 'UUID Validation',
        'validators': {
            **GENERAL_VALIDATION,
        },
    }
}