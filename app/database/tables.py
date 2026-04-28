from datetime import datetime
from uuid import UUID

TABLES_MAP = {
    'client': {
        'fields': {
            'client_id': {
                'is_pk': True,
                'is_unique': True,
                'is_nullable': False,
                'datatype': UUID
            },
            'first_name': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'datatype': str,
            },
            'last_name': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'datatype': str,
            },
            'company_name': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'datatype': str,
            },
            'email': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'datatype': str,
            },
            'phone': {
                'is_pk': False,
                'is_unique': True,
                'is_nullable': False,
                'datatype': str,
            },
            'display_name': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'save'
            },
            'updated_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'update'
            }
        }
    },
    'subscription': {
        'fields': {
            'subscription_id': {
                'is_pk': True,
                'is_unique': True,
                'is_nullable': False,
                'datatype': str,
            },
            'plan_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
                'fk': {
                    'to': 'plan',
                    'on_delete': 'cascade',
                    'on_update': 'no action'
                },
            },
            'client_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
                'fk': {
                    'to': 'client',
                    'on_delete': 'cascade',
                    'on_update': 'no action'
                },
            },
            'plan_unit': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': int,
            },
            'expiration_date': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
            },
            'discount': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': int,
            },
            'discount_type': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
            },
            'vat': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': int,
            },
            'status': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
            },
            'payment_status': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'save'
            },
            'updated_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
                'is_date': True,
                'auto_update': 'update'
            }
        }
    },
    'plan': {
        'fields': {
            'plan_id': {
                'is_pk': True,
                'is_unique': True,
                'is_nullable': False,
                'datatype': UUID,
            },
            'plan_name': {
                'is_pk': False,
                'is_unique': True,
                'is_nullable': False,
                'datatype': str,
            },
            'duration': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': int,
            },
            'plan_type': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': str,
            },
            'slot': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': int,
            },
            'guest_pass': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': int,
            },
            'price': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': int,
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'save'
            },
            'updated_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'update'
            }
        }
    },
    'payment': {
        'fields': {
            'payment_id': {
                'is_pk': True,
                'is_unique': True,
                'is_nullable': False,
                'datatype': UUID,
            },
            'client_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': UUID,
                'fk': {
                    'to': 'client',
                    'on_delete': 'cascade',
                    'on_update': 'no action'
                },
            },
            'subscription_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': UUID,
                'fk': {
                    'to': 'subscription',
                    'on_delete': 'cascade',
                    'on_update': 'no action'
                },
            },
            'amount': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': int,
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'save'
            },
            'updated_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'update'
            }
        }
    },
    'visit': {
        'fields': {
            'visit_id': {
                'is_pk': True,
                'is_unique': True,
                'is_nullable': False,
                'datatype': UUID,
            },
            'subscription_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': UUID,
                'fk': {
                    'to': 'subscription',
                    'on_delete': 'cascade',
                    'on_update': 'no action'
                },
            },
            'client_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': UUID,
                'fk': {
                    'to': 'client',
                    'on_delete': 'cascade',
                    'on_update': 'no action'
                },
            },
            'timestamp': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'save'
            },
        }
    },
    'assigned_client': {
        'fields': {
            'assigned_client_id': {
                'is_pk': True,
                'is_unique': True,
                'is_nullable': False,
                'datatype': UUID,
            },
            'subscription_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': UUID,
                'fk': {
                    'to': 'subscription',
                    'on_delete': 'cascade',
                    'on_update': 'no action'
                },
            },
            'client_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': UUID,
                'fk': {
                    'to': 'client',
                    'on_delete': 'cascade',
                    'on_update': 'no action'
                },
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'datatype': datetime,
                'is_date': True,
                'auto_update': 'save'
            },
        }
    },
}
