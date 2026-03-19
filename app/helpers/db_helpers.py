import os
import sys
import uuid
import inspect
from logs.utils import log_to_file, log_error_to_file
from notification.notification import Notification
import logging

logger = logging.getLogger(__name__)


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
            logging.error(str(err))
            sys.stderr.write(f'\n{err}\n')
            sys.stderr.flush()
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
            INSERT INTO client(client_id, first_name, last_name, company_name, email, phone, display_name, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
    elif model.lower() == 'plan':
        query = '''
            INSERT INTO plan VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        '''
    elif model.lower() == 'payment':
        query = '''
            INSERT INTO payment(
                            payment_id, 
                            client_id, 
                            subscription_id,
                            amount,
                            created_at,
                            updated_at
                        ) 
            VALUES (?, ?, ?, ?, ?, ?);
        '''
    elif model.lower() == 'subscription':
        query = '''
            INSERT INTO subscription VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
    elif model.lower() == 'visit':
        query = '''
            INSERT INTO visit VALUES (?, ?, ?, ?);
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
        logger.error(str(err))
        sys.stderr.write(f'\n{err}\n')
        sys.stderr.flush()
        Notification.send_notification(err)
        exit(1)

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
            UPDATE client SET first_name = ?, last_name = ?, company_name = ?, email = ?, phone = ?, display_name = ?, updated_at = ?
            WHERE client_id = ?;
        '''
    elif model.lower() == 'plan':
        query = '''
            UPDATE plan SET plan_name = ?, duration = ?, plan_type = ?, slot = ?, guest_pass = ?, price = ? WHERE plan_id = ?;
        '''
    elif model.lower() == 'payment':
        query = '''
            UPDATE payment SET client_id = ?, subscription_id = ?, amount = ?, updated_at = ? WHERE payment_id = ?;
        '''
    elif model.lower() == 'subscription':
        query = '''
            UPDATE subscription SET plan_id = ?, client_id = ?, plan_unit = ?, expiration_date = ?,  discount = ?, discount_type = ?, vat = ?, status = ?, payment_status = ?, updated_at = ? WHERE subscription_id = ?;
        ''' 
    else:
        raise ValueError('Invalid model argument')

    try:
        cursor.execute(query, values)
    except Exception as err:
        logging.error(str(err))
        sys.stderr.write(f'\n{err}\n')
        sys.stderr.flush()
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

        entry = cursor.fetchone()
        return entry
    except Exception as err:
        logger.exception(str(err))
        sys.stderr.write(f'\n{err}\n')
        sys.stderr.flush()
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
        entries = cursor.fetchall()

        if col_names:
            # Get column names
            column_names = [description[0] for description in cursor.description]

            return (entries, column_names)
    
        return entries if entries else []
    except Exception as err:
        logger.exception(str(err))
        sys.stderr.write(f'\n{err}\n')
        sys.stderr.flush()
        return None

def delete_db(db_path, db: str):
    if os.path.isfile(db_path / db):
        print(f'Deleting {db}')
        os.remove(db_path / db)

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