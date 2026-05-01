
class Field:

    null = False
    unique = False
    pk = False
    default = None
    __data = None

    def __init__(self, **kwargs):
        self.set_kargs(**kwargs)

    def __str__(self):
        return self.__class__.__name__
    
    def set_kargs(self, **kwargs):
        contraints = get_contraint_keys_by_field_name(self.__class__.__name__)

        for contraint in contraints:
            contraint_value = kwargs.get(contraint, None)
            if contraint_value is not None:
                setattr(self, contraint, contraint_value)
    
    @property
    def field_type(self):
        return None

    def _validate_field(self):
        pass

    
class TextField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'str'
    

class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        on_update = kwargs.get('on_update', False)
        on_save = kwargs.get('on_save', False)

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'datetime'
    

class UUIDField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'UUID'
    

class ForeignKeyField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return self.__class__.__name__
    
    @property
    def field_type(self):
        return 'fk'
    
class JSONField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

