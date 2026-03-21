ACTION_MAP = {
    "run": 'tests'
}

MODULE_MAP = {
    'tests': 'tests.test'
}

BASE_COMMANDS = {
    'test': {
        'name': 'test',
        'module': 'tests.test',
        'require_args': [],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                # TODO: get this values from table.keys
                'validate': lambda values:  set(values) <= {'client', 'plan', 'payment', 'subscription', 'visit'}
            },
        }
    },
    'GET': {
        'name': 'GET',
        'module': 'methods.get',
        'require_args': ['model'],
        'has_args': True,
        'args': {
            'model': {
                'name': 'Model',
                # TODO: get this values from table.keys
                'validate': lambda values:  set(values) <= {'client', 'plan', 'payment', 'subscription', 'visit'}
            },
            'field_id': {
                'name': 'Field ID',
                'field_id': [],
            }
        }
    }

}