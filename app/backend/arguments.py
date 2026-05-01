from database.db import get_table_map
import os

'''
This module holds all the commands, module, and argument validations
'''

TABLES_MAP = get_table_map()
DB_TABLES = set(TABLES_MAP)


DEFAULT_COMMANDS = {
    'CREATE_MODEL': {
        'name': 'CREATE_MODEL',
        'module': 'database.commands',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                
                # 'validate': lambda value:  isinstance(value, str) and value not already existing model file,
                'validate': lambda value:  isinstance(value, str) and not os.path.isfile(os.path.join('models', f'{value}.py')),
                'message': 'Model needs to be a string of model name not already created'
            },
            'payload': {
                'name': 'Payload',
                
                'validate': lambda payload_keys, model:  set(payload_keys) <= {'table_map', 'arguments'} and 'table_map' in payload_keys,
                'message': 'payload is expected to be <= {"table_map", "arguments"} and "table_map" is required'
            },
        }
    },
    'CREATE_BULK_MODELS': {
        'name': 'CREATE_BULK_MODELS',
        'module': 'database.commands',
        'require_args': ['payload'],
        'has_args': True,
        'args': {
            'payload': {
                'name': 'Payload',
                
                'validate': lambda payload_keys, model:  set(payload_keys) <= {'table_maps', 'arguments'} and 'table_maps' in payload_keys,
                'message': 'payload is expected to be <= {"table_maps", "arguments"} and "table_maps" is required'
            },
        }
    },
    'TESTS': {
        'name': 'test',
        'module': 'tests.test',
        'require_args': [],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                
                'validate': lambda value:  value in DB_TABLES,
                'message': 'Model needs to be a string and already declared in table map'
            },
        }
    },
    'CREATE': {
        'name': 'CREATE',
        'module': 'services.main',
        'require_args': ['model'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                
                'validate': lambda value:  value in DB_TABLES,
                'message': 'Model needs to be a string and not already declared in table map'
            },
        }
    },
    'FETCH_ALL': {
        'name': 'FETCH_ALL',
        'module': 'services.main',
        'require_args': ['model'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                
                'validate': lambda value:  value in DB_TABLES,
                'message': 'Model needs to be a string and already declared in table map'
            },
        }
    },
    'FETCH_ONE': {
        'name': 'FETCH_ONE',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                
                'validate': lambda value:  value in DB_TABLES,
                'message': 'Model needs to be a string and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model:  payload_keys <= set(TABLES_MAP.get(model).get('fields').keys()),
                'message': f'Payload data must be <= field_map fields'
            }
        }
    },
    'FILTER': {
        'name': 'FILTER',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                
                'validate': lambda value:  value in DB_TABLES,
                'message': 'Model needs to be a string and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model:  payload_keys <= set(TABLES_MAP.get(model).get('fields').keys()),
                'message': f'Payload data must be <= field_map fields'
            }
        }
    },
    'UPDATE': {
        'name': 'UPDATE',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                
                'validate': lambda value:  value in DB_TABLES,
                'message': 'Model needs to be a string and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model:  payload_keys <= set(TABLES_MAP.get(model).get('fields').keys()) and f'{model}_id' in payload_keys,
                'message': f'Payload data must be <= field_map fields'
            }
        }
    },
    'DELETE': {
        'name': 'DELETE',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                
                'validate': lambda value:  value in DB_TABLES,
                'message': 'Model needs to be a string and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: f'{model}_id' in payload_keys,
                'message': f'Payload data must be == model_id'
            }
        }
    },
}

UTIL_COMMANDS = {
    'GET_FIELD_VALIDATORS' : {
        'name': 'GET_FIELD_VALIDATORS',
        'module': 'database.commands',
        'require_args': [],
        'has_args': True,
        'args': {
            'payload': {
                'name': 'Payload',
                
                'validate': lambda payload_keys, model:  set(payload_keys) <= {'int', 'str', 'UUID', 'dict', 'datetime'},
                'message': "Payload is expected to be <= {'int', 'str', 'UUID', 'dict', 'datetime'}"
            },
        }
    },
}

BASE_COMMANDS = {
    **DEFAULT_COMMANDS,
    **UTIL_COMMANDS,
    'SET_ASSIGNED_CLIENT': {
        'name': 'SET_ASSIGNED_CLIENT',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('subscription') and value in DB_TABLES,
                'message': 'Model needs to be = "subscription" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: 'client_id' in payload_keys,
                'message': 'Payload must contain "client_id" and already declared in table map'
            }
        }
    },
    'REMOVE_ASSIGNED_CLIENT': {
        'name': 'SET_ASSIGNED_CLIENT',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('subscription') and value in DB_TABLES,
                'message': 'Model needs to be = "subscription" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: 'client_id' in payload_keys,
                'message': 'Payload must contain "client_id" and already declared in table map'
            }
        }
    },
    'LOG_CLIENT_TO_VISIT': {
        'name': 'LOG_CLIENT_TO_VISIT',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('subscription') and value in DB_TABLES,
                'message': 'Model needs to be = "subscription" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: 'client_id' in payload_keys,
                'message': 'Payload must contain "client_id" and already declared in table map'
            }
        }
    },
    'REMOVE_USER_VISIT': {
        'name': 'REMOVE_USER_VISIT',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('subscription') and value in DB_TABLES,
                'message': 'Model needs to be = "subscription" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: {'client_id', 'date_value'} == set(payload_keys),
                'message': 'Payload must contain ["client_id", "date_valu"] and already declared in table map'
            }
        }
    },
    'GET_CLIENT_VISITS_PER_SUB': {
        'name': 'GET_CLIENT_VISITS_PER_SUB',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('visit') and value in DB_TABLES,
                'message': 'Model needs to be = "visit" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: payload_keys <= {'sub_id', 'get_count', 'col_names', 'result_only'} and 'sub_id' in payload_keys,
                'message': "Payload needs to contain {'sub_id', 'get_count', 'col_names', 'result_only'}  and sub_id is required"
            }
        }
    },
    'GET_CLIENT_VISITS': {
        'name': 'GET_CLIENT_VISITS',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('visit') and value in DB_TABLES,
                'message': 'Model needs to be = "visit" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: payload_keys <= {'client_id', 'get_count', 'col_names'} and 'client_id' in payload_keys,
                'message': "Payload needs to contain {'client_id', 'get_count', 'col_names'} and 'client_id' is required"
            }
        }
    },
    'FILTER_SUB': {
        'name': 'FILTER_SUB',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('visit') and value in DB_TABLES,
                'message': 'Model needs to be = "visit" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: payload_keys <= {'value', 'col_names'} and 'value' in payload_keys,
                'message': "Payload needs to contain {'value', 'col_names'} and 'value' is required"
            }
        }
    },
    'GET_ALL_SUB_VISITS_COUNT': {
        'name': 'GET_ALL_SUB_VISITS_COUNT',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('visit') and value in DB_TABLES,
                'message': 'Model needs to be = "visit" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: 'sub_id' in payload_keys,
                'message': "Payload require 'sub_id'"
            }
        }
    },
    'EXPORT_MODEL': {
        'name': 'EXPORT_MODEL',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in DB_TABLES,
                'message': 'Model needs to be = "visit" and already declared in table map'
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: payload_keys <= {'file_type', 'path', 'sub_id'},
                'message': "Payload needs to contain {'file_type', 'path', 'sub_id'}"
            }
        }
    },
}