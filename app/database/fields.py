from utils.general import is_valid_date, matches_regex

class Field:

    null = False
    unique = False
    pk = False
    default = None
    __data = None

    _validator_map = {
        'null': {
            'func': lambda value, arg=None: value is not None,
            'message': 'NOT NULL CONSTRAINT BROKEN with value {value}'
        },
        'unique': {
            'func': lambda value, arg=None: value_exist_in_field(value, arg),
            'message': 'UNIQUE CONSTRAINT BROKEN with value {value}'
        }
    }

    def __init__(self, **kwargs):
        self.set_kargs(**kwargs)

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def data(self):
        return self.__data
    
    def set_kargs(self, **kwargs):
        contraints = get_contraint_keys_by_field_name(self.__class__.__name__)

        default_value = None
        for contraint in contraints:
            contraint_value = kwargs.get(contraint, None)
            if contraint_value is not None:
                setattr(self, contraint, contraint_value)

            if contraint == 'default' and contraint_value is not None:
                self._set_data(contraint_value)

    def _set_data(self, new_data):
        data = new_data
        if isinstance(new_data, Field):
            data = new_data.data

        self._validate_data(data)
        self.__data = data

    def _validate_data(self, data):
        contraints = get_contraint_keys_by_field_name(self.__class__.__name__)
        for contraint in contraints:
            if hasattr(self, contraint):
                self.__validate_by_contraint(contraint, data)

    def __validate_by_contraint(self, contraint, data):
        validator = self.__get_validator(contraint)
        if validator:
            contraint_value = getattr(self, contraint)
            is_valid = validator['func'](data, contraint_value)

            if not is_valid:
                raise Exception(validator['message'].format(value=data))
            

    def __get_validator(self, constraint):
        return self._validator_map.get(constraint, None)
    
    @property
    def field_type(self):
        return None

    def _validate_field(self):
        pass

    
class TextField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._validator_map = {
            **self._validator_map,
            'digit': {
                'func': lambda value, exp_value: isinstance(value, str) and value.isdigit(),
                'message': 'DIGIT CONSTRAINT BROKEN with value {value}'
            },
            'alpha': {
                'func': lambda value, exp_value: isinstance(value, str) and value.isalpha(),
                'message': 'ALPHA CONSTRAINT BROKEN with value {value}'
            },
            'alphanum': {
                'func': lambda value, exp_value: isinstance(value, str) and value.isalnum(),
                'message': 'ALPHANUM CONSTRAINT BROKEN with value {value}'
            },
            'max_length': {
                'func': lambda value, max: not len(value) > max,
                'message': 'MAX LENGTH CONSTRAINT BROKEN with value {value}'
            },
            'min_length': {
                'func': lambda value, min: not len(value) < min,
                'message': 'MIN LENGTH CONSTRAINT BROKEN with value {value}'
            },
            'character_length': {
                'func': lambda value, length: not len(value) > length,
                'message': 'CHAR LENGTH CONSTRAINT BROKEN with value {value}'
            },
            'choice': {
                'func': lambda value, values_list: value in set(values_list),
                'message': 'CHOICE CONSTRAINT BROKEN with value {value}'
            },
            'regex_full_match': {
                'func': lambda value, pattern: matches_regex(value, pattern),
                'message': 'FULL MATCH CONSTRAINT BROKEN with value {value}'

            },
            'regex_partial_match': {
                'func': lambda value, pattern: matches_regex(value, pattern, partial=True),
                'message': 'PARTIAL MATCH CONSTRAINT BROKEN with value {value}'
            }
        }

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'str'
    

class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validator_map = {
            **self._validator_map,
            'gt': {
                'func': lambda value, num: value > num,
                'message': 'GREATER THAN CONSTRAINT BROKEN with value {value}'
            },
            'lt': {
                'func': lambda value, num: value < num,
                'message': 'LESS THAN CONSTRAINT BROKEN with value {value}'
            },
            'range': {
                'func': lambda value, values_list: value in values_list,
                'message': 'RANGE CONSTRAINT BROKEN with value {value}'
            }
        }

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'int'
    

class DateTimeField(Field):
    on_update = False
    on_save = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validator_map = {
            **self._validator_map,

        }

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'datetime'
    

class UUIDField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validator_map = {
            **self._validator_map,
            
        }

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'UUID'
    

class ForeignKeyField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validator_map = {
            **self._validator_map,
            
        }

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'fk'
    
class JSONField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validator_map = {
            **self._validator_map,
            
        }

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'json'
    

def get_field_from_datatype(datatype):
    field = None
    match datatype:
        case 'UUID':
            field = 'UUIDField'
        case 'str':
            field = 'TextField'
        case 'int':
            field = 'IntegerField'
        case 'datetime':
            field = 'DateTimeField'
        case 'fk':
            field = 'ForeignKeyField'
        case 'json':
            field = 'JSONField'
    return field

def get_contraint_keys_by_field_name(field):
    default_contraint = ['pk', 'null', 'unique', 'default', 'datatype']

    contraint_key_map = {
        'UUIDField': set(default_contraint),
        'TextField': set([*default_contraint, 'digit', 'alpha', 'alphanum', 'max_length', 'min_length', 'choice', 'regex_full_match', 'regex_partial_match']),
        'IntegerField': set([*default_contraint, 'gt', 'lt', 'range']),
        'DateTimeField': set([*default_contraint, 'on_update', 'on_save']),
        'ForeignKeyField': set([*default_contraint, 'to', 'on_delete', 'on_update', 'pk_only', 'lazy']),
        'JSONField': set([*default_contraint, 'indent']),
    }

    contraint_keys = contraint_key_map.get(field, None)
    if not contraint_keys:
        raise Exception(f'There is no contraint key for field {field}')
    
    return contraint_keys

def get_required_datatypes():
    return {'str', 'int', 'datetime', 'fk', 'UUID', 'json'}

def value_exist_in_field(value, args):
    return True

