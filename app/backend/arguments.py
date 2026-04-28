from database.tables import TABLES_MAP

ACTION_MAP = {
    "run": 'tests'
}

MODULE_MAP = {
    'tests': 'tests.test'
}

BASE_COMMANDS = {
    'TESTS': {
        'name': 'test',
        'module': 'tests.test',
        'require_args': [],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                # TODO: get this values from table.keys
                'validate': lambda value:  value in {'client', 'plan', 'payment', 'subscription', 'visit'}
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
                # TODO: get this values from table.keys
                'validate': lambda value:  value in {'client', 'plan', 'payment', 'subscription', 'visit'}
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
                # TODO: get this values from table.keys
                'validate': lambda value:  value in {'client', 'plan', 'payment', 'subscription', 'visit'}
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
                # TODO: get this values from table.keys
                'validate': lambda value:  value in {'client', 'plan', 'payment', 'subscription', 'visit'}
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model:  payload_keys <= set(TABLES_MAP.get(model).get('fields').keys()),
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
                # TODO: get this values from table.keys
                'validate': lambda value:  value in {'client', 'plan', 'payment', 'subscription', 'visit'}
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model:  payload_keys <= set(TABLES_MAP.get(model).get('fields').keys()),
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
                # TODO: get this values from table.keys
                'validate': lambda value:  value in {'client', 'plan', 'payment', 'subscription', 'visit'}
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model:  payload_keys <= set(TABLES_MAP.get(model).get('fields').keys()) and f'{model}_id' in payload_keys,
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
                # TODO: get this values from table.keys
                'validate': lambda value:  value in {'client', 'plan', 'payment', 'subscription', 'visit'}
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: f'{model}_id' in payload_keys,
            }
        }
    },
    'SET_ASSIGNED_CLIENT': {
        'name': 'SET_ASSIGNED_CLIENT',
        'module': 'services.main',
        'require_args': ['model', 'payload'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                'validate': lambda value:  value in set('subscription')
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: 'client_id' in payload_keys,
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
                'validate': lambda value:  value in set('subscription')
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: 'client_id' in payload_keys,
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
                'validate': lambda value:  value in set('subscription')
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: 'client_id' in payload_keys,
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
                'validate': lambda value:  value in set('subscription')
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: {'client_id', 'date_value'} == set(payload_keys),
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
                'validate': lambda value:  value in set('visit')
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: payload_keys <= {'sub_id', 'get_count', 'col_names', 'result_only'} and 'sub_id' in payload_keys,
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
                'validate': lambda value:  value in set('visit')
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: payload_keys <= {'client_id', 'get_count', 'col_names'} and 'client_id' in payload_keys,
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
                'validate': lambda value:  value in set('visit')
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: payload_keys <= {'value', 'col_names'} and 'value' in payload_keys,
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
                'validate': lambda value:  value in set('visit')
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: 'sub_id' in payload_keys,
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
                'validate': lambda value:  value in {'client', 'plan', 'subscription', 'visit'}
            },
            'payload': {
                'name': 'payload',
                'validate': lambda payload_keys, model: payload_keys <= {'file_type', 'path', 'sub_id'},
            }
        }
    },

}