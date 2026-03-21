TABLES_MAP = {
    'client': {
        'fields': {
            'client_id': {
                'is_pk': True,
                'is_unique': True,
                'is_nullable': False,
                'data_type': str,
            },
            'first_name': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
            },
            'last_name': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
            },
            'company_name': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
            },
            'email': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
            },
            'phone': {
                'is_pk': False,
                'is_unique': True,
                'is_nullable': False,
                'data_type': str,
            },
            'display_name': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_date': True,
                'auto_update': 'save'
            },
            'updated_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
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
                'data_type': str,
            },
            'plan_name': {
                'is_pk': False,
                'is_unique': True,
                'is_nullable': False,
                'data_type': str,
            },
            'duration': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': int,
            },
            'plan_type': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
            },
            'slot': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': int,
            },
            'guest_pass': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': int,
            },
            'price': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': int,
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
                'is_date': True,
                'auto_update': 'save'
            },
            'updated_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
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
                'data_type': str,
            },
            'plan_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_fk': True,
                'to': 'plan'
            },
            'client_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_fk': True,
                'to': 'client'
            },
            'plan_unit': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': int,
            },
            'expiration_date': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
            },
            'discount': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': int,
            },
            'discount_type': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
            },
            'vat': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': int,
            },
            'status': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
            },
            'payment_status': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
                'is_date': True,
                'auto_update': 'save'
            },
            'updated_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
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
                'data_type': str,
            },
            'client_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_fk': True,
                'to': 'client'
            },
            'subscription_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_fk': True,
                'to': 'subscription'
            },
            'amount': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': int,
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
                'is_date': True,
                'auto_update': 'save'
            },
            'updated_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': True,
                'data_type': str,
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
                'data_type': str,
            },
            'subscription_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_fk': True,
                'to': 'subscription'
            },
            'client_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_fk': True,
                'to': 'client'
            },
            'timestamp': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
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
                'data_type': str
            },
            'subscription_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_fk': True,
                'to': 'subscription'
            },
            'client_id': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_fk': True,
                'to': 'client'
            },
            'created_at': {
                'is_pk': False,
                'is_unique': False,
                'is_nullable': False,
                'data_type': str,
                'is_date': True,
                'auto_update': 'save'
            },
        }
    },
}
