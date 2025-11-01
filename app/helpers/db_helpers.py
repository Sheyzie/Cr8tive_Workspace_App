import uuid
from logs.utils import log_to_file, log_error_to_file
from notification.notification import Notification


def generate_id(model: str, cursor) -> str:
    if not model:
        return None
    if not hasattr(cursor, 'execute'):
        return None
    
    id_exist = True
    id_string = ""
    while id_exist:
        try:
            id_string = str(uuid.uuid4())
            query = f'''
                SELECT * FROM {model.lower()} WHERE {model.lower()}_id = ?;
            '''

            cursor.execute(query, (id_string,))
            entry = cursor.fetchone()

            if not entry:
                id_exist = False
        except Exception as err:
            log_error_to_file(model.capitalize(), 'Error', f"Error generating ID @ {__name__} 'line 27'")
            log_error_to_file(model.capitalize(), 'Error', f'{err}')
            log_to_file(model.capitalize(), 'Error', f"Error generating ID @ {__name__} 'line 29'")
            return None
    return id_string

def insert_to_db(model: str, cursor, values, many=False) -> None:
    if not model:
        raise ValueError('No Model provide for insert')
    if not hasattr(cursor, 'execute'):
        raise ValueError('Invalid cursor object')

    if len(values) == 0:
        raise ValueError('Insert values cannot be zero')

    query = ''

    if model.lower() == 'client':
        query = '''
            INSERT INTO client(client_id, first_name, last_name, company_name, email, phone, created_at) VALUES(?, ?, ?, ?, ?, ?, ?);
        '''
    elif model.lower() == 'plan':
        query = '''
            INSERT INTO plan VALUES (?, ?, ?, ?, ?, ?);
        '''
    elif model.lower() == 'payment':
        query = '''
            INSERT INTO payment VALUES (?, ?, ?, ?, ?, ?);
        '''
    elif model.lower() == 'subscription':
        query = '''
            INSERT INTO subscription VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        '''
    elif model.lower() == 'visit':
        query = '''
            INSERT INTO visit VALUES (?, ?, ?);
        '''
    elif model.lower() == 'assigned_client':
        query = '''
            INSERT INTO assigned_client VALUES (?, ?, ?);
        '''
    else:
        raise ValueError('Invalid model argument')
    
    try:
        if many:
            cursor.executemany(query, values)
        else:
            cursor.execute(query, values)
    except Exception as err:
        log_error_to_file(model.capitalize(), 'Error', f"Error inserting {model.lower()} from db @ {__name__} 'line 77'")
        log_error_to_file(model.capitalize(), 'Error', f'{err}')
        log_to_file(model.capitalize(), 'Error',f"Error inserting {model.lower()} from db @ {__name__} 'line 79'")
        Notification.send_notification(err)

def update_in_db(model: str, cursor, values) -> None:
    if not model:
        raise ValueError('No Model provide for update')
    if not hasattr(cursor, 'execute'):
        raise ValueError('Invalid cursor object')

    if len(values) == 0:
        raise ValueError('Update values cannot be zero')
    
    query = ''

    if model.lower() == 'client':    
        query = '''
            UPDATE client SET first_name = ?, last_name = ?, company_name = ?, email = ?, phone = ? 
            WHERE client_id = ?;
        '''
    elif model.lower() == 'plan':
        query = '''
            UPDATE plan SET plan_name = ?, duration = ?, plan_type = ?, price = ? WHERE plan_id = ?;
        '''
    elif model.lower() == 'payment':
        query = '''
            UPDATE payment SET discount = ?, tax = ?, total_price = ?, amount_paid = ? WHERE payment_id = ?;
        '''
    elif model.lower() == 'subscription':
        query = '''
            UPDATE subscription SET plan_id = ?, client_id = ?, expiration = ?, status = ?, updated_at = ? WHERE subscription_id = ?;
        '''
    else:
        raise ValueError('Invalid model argument')

    try:
        cursor.execute(query, values)
    except Exception as err:
        log_error_to_file(model.capitalize(), 'Error', f"Error updating {model.lower()} from db @ {__name__} 'line 116'")
        log_error_to_file(model.capitalize(), 'Error', f'{err}')
        log_to_file(model.capitalize(), 'Error', f"Error updating {model.lower()} from db @ {__name__} 'line 118'")
        Notification.send_notification(err)

def fetch_one_entry(model: str, cursor, value, by_name=False, by_phone=False, by_email=False):
    if not model:
        raise ValueError('No Model provide for update')
    if not hasattr(cursor, 'execute'):
        raise ValueError('Invalid cursor object')
    if not value:
        raise ValueError('Value is required')
    
    query = f'''
        SELECT * FROM {model.lower()} WHERE {model.lower()}_id = ?;
    '''

    if by_name:
        query = f'''
            SELECT * FROM {model.lower()}  WHERE {model.lower()}_name = ?;
        '''
    elif by_phone and model.lower() == 'client':
        query = '''
            SELECT * FROM client WHERE phone = ?;
        '''

    elif by_email and model.lower() == 'client':
        query = '''
            SELECT * FROM client WHERE email = ?;
        '''

    try:
        cursor.execute(query, (value,))

        data = cursor.fetchone()
    
        if data:
            log_to_file(model.capitalize(), 'Success', f"Fetch data from db @ {__name__} 'line 153'")
            return data
        else:
            return None
    except Exception as err:
        log_to_file(model.capitalize(), 'Error', f"Error getting {model.lower()} from db @ {__name__} 'line 158'")
        log_error_to_file(model.capitalize(), 'Error', f"Error getting {model.lower()} from db @ {__name__} 'line 159'")
        log_error_to_file(model.capitalize(), 'Error', f'{err}')
        return None
    
def fetch_all_entry(model: str, cursor, col_names=False):
    if not model:
        raise ValueError('No Model provide for update')
    if not hasattr(cursor, 'execute'):
        raise ValueError('Invalid cursor object')
    
    query = f'''
        SELECT * FROM {model.lower()};
    '''

    try:
        cursor.execute(query)

        clients = cursor.fetchall()

        if col_names:
            # Get column names
            column_names = [description[0] for description in cursor.description]
            log_to_file(model.capitalize(), 'Success', f"Fetch data from db @ {__name__} 'line 183'")
            
            return (clients, column_names) if clients else []
    
        log_to_file(model.capitalize(), 'Success', f"Fetch data from db @ {__name__} 'line 183'")
        return clients if clients else []
    except Exception as err:
        log_to_file(model.capitalize(), 'Error', f"Error getting {model.lower()} from db @ {__name__} 'line 186'")
        log_error_to_file(model.capitalize(), 'Error', f"Error getting {model.lower()} from db @ {__name__} 'line 187'")
        log_error_to_file(model.capitalize(), 'Error', f'{err}')
        print(err)
        return None
    
# def validate_model_data(model: str, data):
#     fields = None
    
#     if model.lower() == 'client':
#         fields = [
#             (
#                 'first_name', [
#                     lambda f_name: isinstance(f_name, str) and len(f_name) > 3
#                 ]
#             ),
#             (
#                 'last_name', [
#                     lambda f_name: isinstance(f_name, str) and len(f_name) > 3
#                 ]
#             ),
#         ]