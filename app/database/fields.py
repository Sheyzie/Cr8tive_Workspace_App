from utils.general import is_valid_date, matches_regex

class Field:

    null = False
    unique = False
    pk = False
    default = None
    _data = None

    _validator_map = {
        'null': {
            'func': lambda value, arg=None: value is not None,
            'message': 'NOT NULL CONSTRAINT BROKEN with value {value} on {contraint} contraint'
        },
        'unique': {
            'func': lambda value, arg=None: value_exist_in_field(value, arg),
            'message': 'UNIQUE CONSTRAINT BROKEN with value {value} on {contraint} contraint'
        }
    }

    def __init__(self, **kwargs):
        self.set_kargs(**kwargs)

    def __str__(self):
        return f'{self.data}'
    
    def __repr__(self):
        if isinstance(self.data, (str, int, float)):
            return f'{self.data}'
        return f'{self}'
    
    def __eq__(self, value):
        return self.data == value
    
    @property
    def data(self):
        return f'{self._data}'
    
    @data.setter
    def data(self, newdata):
        self._validate_data(newdata)
        self._data = newdata
        return self.data
    
    def set_kargs(self, **kwargs):
        contraints = get_contraint_keys_by_field_name(self.__class__.__name__)

        default_value = None
        for contraint in contraints:
            contraint_value = kwargs.get(contraint, None)
            if contraint_value is not None:
                setattr(self, contraint, contraint_value)

            if contraint == 'default' and contraint_value is not None:
                self._set_data(contraint_value)

    def _set_data(self, new_data, attr_name=None):
        data = new_data
        if isinstance(new_data, Field):
            data = new_data.data

        self._validate_data(data, attr_name)
        self._data = data
        return data

    def _reset_data(self):
        self._data = None

    def _validate_data(self, data, attr_name=None):
        field = self.__class__.__name__
        contraints = get_contraint_keys_by_field_name(field)
        for contraint in contraints:
            if hasattr(self, contraint):
                self._validate_by_contraint(contraint, data, field=field, attr_name=attr_name)

    def _validate_by_contraint(self, contraint, data, field='field', attr_name=None):
        validator = self._get_validator(contraint)
        if validator:
            contraint_value = getattr(self, contraint)
            is_valid = validator['func'](data, contraint_value)

            if not is_valid:
                message = validator['message'] + f' on {attr_name}' if attr_name else validator['message']
                raise Exception(message.format(value=data, contraint=field))
            
    def _get_validator(self, constraint):
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
                'message': 'DIGIT CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'alpha': {
                'func': lambda value, exp_value: isinstance(value, str) and value.isalpha(),
                'message': 'ALPHA CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'alphanum': {
                'func': lambda value, exp_value: isinstance(value, str) and value.isalnum(),
                'message': 'ALPHANUM CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'max_length': {
                'func': lambda value, max: not len(value) > max,
                'message': 'MAX LENGTH CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'min_length': {
                'func': lambda value, min: not len(value) < min,
                'message': 'MIN LENGTH CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'character_length': {
                'func': lambda value, length: not len(value) > length,
                'message': 'CHAR LENGTH CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'choice': {
                'func': lambda value, values_list: value in set(values_list),
                'message': 'CHOICE CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'regex_full_match': {
                'func': lambda value, pattern: matches_regex(value, pattern),
                'message': 'FULL MATCH CONSTRAINT BROKEN with value {value} on {contraint} contraint'

            },
            'regex_partial_match': {
                'func': lambda value, pattern: matches_regex(value, pattern, partial=True),
                'message': 'PARTIAL MATCH CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            }
        }

    def __str__(self):
        return f'{self.data}'
    
    def __len__(self):
        if self._data is None:
            return 0
        return len(self._data)
    
    def __iter__(self):
        for char in self._data:
            yield char
    
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
                'message': 'GREATER THAN CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'lt': {
                'func': lambda value, num: value < num,
                'message': 'LESS THAN CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'min_value': {
                'func': lambda value, num: value >= num,
                'message': 'MIN VALUE CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'max_value': {
                'func': lambda value, num: value <= num,
                'message': 'MIN VALUE CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            },
            'range': {
                'func': lambda value, values_list: value in values_list,
                'message': 'RANGE CONSTRAINT BROKEN with value {value} on {contraint} contraint'
            }
        }

    def __str__(self):
        return f'{self.data}'
    
    def __add__(self, other):
        if isinstance(other, Field):
            return self._data + other._data
        
        return self._data + other
    
    def __sub__(self, other):
        if isinstance(other, Field):
            return self._data - other._data
        return self._data - other
    
    def __mul__(self, other):
        if isinstance(other, Field):
            return self._data * other._data
        return self._data * other
    
    def __truediv__(self, other):
        if isinstance(other, Field):
            return self._data / other._data
        return self._data / other
    
    def __floordiv__(self, other):
        if isinstance(other, Field):
            return self._data // other._data
        return self._data // other
    
    def __mod__(self, other):
        if isinstance(other, Field):
            return self._data % other._data
        return self._data % other
    
    def __pow__(self, other):
        if isinstance(other, Field):
            return self._data ** other._data
        return self._data ** other
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __rsub__(self, other):
        if isinstance(other, Field):
            return other._data - self._data
        return other - self._data
    
    def __rmul__(self, other):
        if isinstance(other, Field):
            return other._data * self._data
        return other * self._data
    
    def __rtruediv__(self, other):
        if isinstance(other, Field):
            return other._data / self._data
        return other / self._data
    
    def __rfloordiv__(self, other):
        if isinstance(other, Field):
            return other._data // self._data
        return other // self._data
    
    def __rmod__(self, other):
        if isinstance(other, Field):
            return other._data % self._data
        return other % self._data
    
    def __rpow__(self, other):
        if isinstance(other, Field):
            return other._data ** self._data
        return other ** self._data
    
    def __iadd__(self, other):
        if isinstance(other, Field):
            self._data += other._data
        self._data += other
        return self

    def __isub__(self, other):
        if isinstance(other, Field):
            self._data -= other._data
        self._data -= other
        return self

    def __imul__(self, other):
        if isinstance(other, Field):
            self._data *= other._data
        self._data *= other
        return self

    def __itruediv__(self, other):
        if isinstance(other, Field):
            self._data /= other._data
        self._data /= other
        return self

    def __neg__(self):
        return -self._data
    
    def __pos__(self):
        return +self._data
    
    def __abs__(self):
        return abs(self._data)
    
    @property
    def field_type(self):
        return 'int'
    

class DateTimeField(Field):
    on_update = False
    on_save = False
    offset = False
    offset_type = 'days' # hours || days || weeks || months || years
    offset_by = 0
    multiply_by = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.offset_type not in {'hours', 'days', 'weeks', 'months', 'years'}:
            raise Exception(f'Invalid offset_type {self.field_type} for DateTimeField expect value in {"{'hours', 'days', 'weeks', 'months', 'years'}"}')
        self._validator_map = {
            **self._validator_map,

        }

    def __str__(self):
        return f'{self.data}'
    
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
        return f'{self.data}'
    
    @property
    def field_type(self):
        return 'UUID'
    

class ForeignKeyField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from database.db import InitDB

        self._validator_map = {
            **self._validator_map,
            'is_model_instance': lambda value, instance=None: isinstance(value, InitDB)
        }

    def __str__(self):
        return f'{self.data}'
    
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
        return f'{self.data}'
    
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
        'DateTimeField': set([*default_contraint, 'on_update', 'on_save', 'offset', 'offset_type', 'offset_by', 'multiply_by']),
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

