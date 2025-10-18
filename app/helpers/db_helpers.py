import uuid
from logs.utils import log_to_file, log_error_to_file
from notification.notification import Notification


def generate_id(model: str, cursor, values) -> str:
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
                SELECT * FROM {model.lower()} WHERE {model.lower()}_id = %s
            '''
            cursor.execute(query, (id_string,))
            entry = cursor.fetchone()
            
            if not entry:
                id_exist = False
        except Exception as err:
            log_error_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()}')
            log_error_to_file(model.capitalize(), 'Error', f'{err}')
            log_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()}')
            return None
    return id_string

def insert_to_db(model: str, cursor, values) -> None:
    if not model:
        raise ValueError('No Model provide for insert')
    if not hasattr(cursor, 'execute'):
        raise ValueError('Invalid cursor object')

    if len(values) == 0:
        raise ValueError('Insert values cannot be zero')
    
    query = ''

    if model.lower() == 'client':
        query = '''
            INSERT INTO client VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''
    elif model.lower() == 'plan':
        query = '''
            INSERT INTO plan VALUES (%s, %s, %s, %s, %s, %s);
        '''
    elif model.lower() == 'payment':
        query = '''
            INSERT INTO payment VALUES (%s, %s, %s, %s, %s, %s);
        '''
    elif model.lower() == 'subscription':
        query = '''
            INSERT INTO subscription VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        '''
    else:
        raise ValueError('Invalid model argument')
    
    try:
        cursor.execute(query)
    except Exception as err:
        log_error_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()}')
        log_error_to_file(model.capitalize(), 'Error', f'{err}')
        log_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()}')
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
            UPDATE client SET first_name = %s, last_name = %s, company_name = %s, email = %s, phone = %s WHERE client_id = %s;
        '''
    elif model.lower() == 'plan':
        query = '''
            UPDATE plan SET plan_name = %s, duration = %s, plan_type = %s, price = %s WHERE plan_id = %s;
        '''
    elif model.lower() == 'payment':
        query = '''
            UPDATE payment SET discount = %s, tax = %s, total_price = %s, amount_paid = %s WHERE payment_id = %s;
        '''
    elif model.lower() == 'subscription':
        query = '''
            UPDATE subscription SET plan_id = %s, client_id = %s, expiration = %s, status = %s, updated_at = %s WHERE subscription_id = %s;
        '''
    else:
        raise ValueError('Invalid model argument')
    
    try:
        cursor.execute(query)
        cursor.close()
    except Exception as err:
        log_error_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()}')
        log_error_to_file(model.capitalize(), 'Error', f'{err}')
        log_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()}')
        Notification.send_notification(err)

def fetch_one_entry(model: str, cursor, value, by_name=False, by_phone=False, by_email=False):
    if not model:
        raise ValueError('No Model provide for update')
    if not hasattr(cursor, 'execute'):
        raise ValueError('Invalid cursor object')
    if not value:
        raise ValueError('Value is required')
    
    query = f'''
        SELECT * FROM {model.lower()} WHERE {model.lower()}_id = %s;
    '''

    if by_name:
        query = f'''
            SELECT * FROM {model.lower()}  WHERE {model.lower()}_name = %s;
        '''
    elif by_phone and model.lower() == 'client':
        query = '''
            SELECT * FROM client WHERE phone = %s;
        '''

    elif by_email and model.lower() == 'client':
        query = '''
            SELECT * FROM client WHERE email = %s;
        '''

    try:
        cursor.execute(query, (value,))

        data = cursor.fetchone()

        if data:
            return data
        else:
            return None
    except Exception as err:
        log_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()} from db')
        log_error_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()} from db')
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
            clients = (clients, column_names)
        return clients if clients else []
    except Exception as err:
        log_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()} from db')
        log_error_to_file(model.capitalize(), 'Error', f'Error getting {model.lower()} from db')
        log_error_to_file(model.capitalize(), 'Error', f'{err}')
        return None