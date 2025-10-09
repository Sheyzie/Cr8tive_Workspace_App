import uuid
from pathlib import Path

from database.db import InitDB
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from utils.export_file import ExportManager
from helpers.export_helper import export_helper
from helpers.db_helpers import generate_id
from notification.notification import Notification
from helpers.db_helpers import (
    generate_id, 
    insert_to_db, 
    update_in_db, 
    fetch_one_entry, 
    fetch_all_entry
)


class Payment(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.payment_id = None
        self.discount = None
        self.tax = None
        self.total_price = None
        self.amount_paid = None
        self.created_at = None
        if kwargs:
            self._get_from_kwargs(kwargs)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

    def _get_from_kwargs(self, **kwargs):
        payment_id = kwargs.get('payment_id')
        if payment_id:
            self.payment_id = payment_id

        discount = kwargs.get('discount')
        if discount:
            self.discount = discount

        tax = kwargs.get('tax')
        if tax:
            self.tax = tax
        
        total_price = kwargs.get('total_price')
        if total_price:
            self.type = total_price.strip()

        amount_paid = kwargs.get('amount_paid')
        if amount_paid:
            self.amount_paid = amount_paid

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

    def _validate(self, check_id=False):
        if check_id:
            if not self.payment_id:
                raise ValidationError('Payment ID is required')
        if not self.discount:
            raise ValidationError('Payment discount is required')
        if self.discount < 0:
            raise ValidationError('Payment discount cannot be less than zero')
        if not isinstance(self.discount, (int, float)):
            raise ValidationError('Payment discount cannot be letters')
        if not self.tax:
            raise ValidationError('Payment tax is required')
        if self.tax < 0:
            raise ValidationError('Payment tax cannot be less than zero')
        if not isinstance(self.tax, (int, float)):
            raise ValidationError('Payment tax cannot be letters')
        if not self.total_price:
            raise ValidationError('Payment total_price is required')
        if self.total_price < 0:
            raise ValidationError('Payment total_price cannot be less than zero')
        if not isinstance(self.total_price, (int, float)):
            raise ValidationError('Payment total_price cannot be letters')
        if not self.amount_paid:
            raise ValidationError('Payment amount_paid is required')
        if self.amount_paid < 0:
            raise ValidationError('Payment amount_paid cannot be less than zero')
        if not isinstance(self.amount_paid, (int, float)):
            raise ValidationError('Payment amount_paid cannot be letters')
    
    def get_id(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            id_string = generate_id('payment', cursor)
            
            if not id_string:
                raise GenerationError('Error generating Payment ID')
            
            self.payment_id = id_string
            
            log_to_file('Plan', 'Success', f'Payment ID generated')
            
            cursor.close()
            self.conn.close()

        
    def save_to_db(self, update=False):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            try:
                if update:
                    values = (self.plan_name, self.duration, self.type, self.price, self.plan_id)
                    update_in_db('plan', cursor, values)
                    return

                values = (self.plan_id, self.plan_name, self.duration, self.type, self.price)
                insert_to_db('plan', cursor, values)
            except ValueError as err:
                log_error_to_file('Plan', 'Error', f'Error saving plan')
                log_error_to_file('Plan', 'Error', f'{err}')
                log_to_file('Plan', 'Error', f'Error saving plan')
                Notification.send_notification(err)

    # TODO: setup payment    
    @classmethod
    def fetch_one(cls, value, by_name=False):
        conn = cls._connect_to_db()
        cursor = conn.cursor(dictionary=True)
        
        
        try:
            payment_data = fetch_one_entry('payment', cursor, value, by_name)

            if payment_data:
                payment = Payment(**payment_data)
                return payment
            else:
                return None
        except Exception as err:
            log_to_file('Payment', 'Error', f'Error getting payment from db')
            log_error_to_file('Payment', 'Error', f'Error getting payment from db')
            log_error_to_file('Payment', 'Error', f'{err}')
            return None

    @classmethod
    def fetch_all(cls):
        conn = cls._connect_to_db()
        cursor = conn.cursor(dictionary=True)
        try:
            clients = fetch_all_entry('payment', cursor)
            return clients
        except Exception as err:
            log_to_file('Payment', 'Error', f'Error getting payment from db')
            log_error_to_file('Payment', 'Error', f'Error getting payment from db')
            log_error_to_file('Payment', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_by_date(cls, value):
        conn = cls._connect_to_db()
        try:
            if conn:
                cursor = conn.cursor(dictionary=True)
               
                query = '''
                    SELECT * FROM payment WHERE created_at LIKE %s;
                '''
                cursor.execute(query, ('%' + value + '%',))

                clients = cursor.fetchall()

                return clients
        except Exception as err:
            log_to_file('Payment', 'Error', f'Error getting payments from db')
            log_error_to_file('Payments', 'Error', f'Error getting payments from db')
            log_error_to_file('Payments', 'Error', f'{err}')
            return None

    