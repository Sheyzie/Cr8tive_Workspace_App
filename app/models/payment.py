import time
import inspect
from database.db import InitDB
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
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
    def __init__(self, using=None, **kwargs):
        super().__init__(using=using)
        self.payment_id = None
        self.discount = 0
        self.tax = 0
        self.total_price = 0
        self.amount_paid = 0
        self.created_at = None
        
        if kwargs:
            data = kwargs.get('kwargs')
            self._get_from_kwargs(kwargs=data)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

    def __str__(self):
        return f'Total Price: {self.total_price}, Amount Paid: {self.amount_paid}'

    def _get_from_kwargs(self, **kwargs):
        data = kwargs.get('kwargs')
        payment_id = data.get('payment_id')
        if payment_id:
            self.payment_id = payment_id

        discount = data.get('discount')
        if discount and isinstance(discount, (int, float)):
            self.discount = discount

        tax = data.get('tax')
        if tax and isinstance(tax, (int, float)):
            self.tax = tax
        
        total_price = data.get('total_price')
        if total_price and isinstance(total_price, (int, float)):
            self.total_price = total_price

        amount_paid = data.get('amount_paid')
        if amount_paid and isinstance(amount_paid, (int, float)):
            self.amount_paid = amount_paid

        created_at = data.get('created_at')
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
            cursor = self.conn.cursor()
            id_string = generate_id('payment', cursor)
            
            if not id_string:
                raise GenerationError('Error generating Payment ID')
            
            self.payment_id = id_string
            
            log_to_file('Payment', 'Success', f'Payment ID generated')
            
            cursor.close()
            self.conn.close()
    
    def save_to_db(self, update=False):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    # convert float to int for precision
                    values = (int(self.discount * 100), int(self.tax * 100), int(self.total_price * 100), int(self.amount_paid * 100), self.payment_id)
                    update_in_db('payment', cursor, values)
                    self.conn.commit()
                    self.conn.close()
                    return

                # convert float to int for precision
                values = (self.payment_id, int(self.discount * 100), int(self.tax * 100), int(self.total_price * 100), int(self.amount_paid * 100), created_at)
                insert_to_db('payment', cursor, values)
                self.conn.commit()
                self.conn.close()
            except ValueError as err:
                log_error_to_file('Payment', 'Error', f"Error saving payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                log_error_to_file('Payment', 'Error', f'{err}')
                log_to_file('Payment', 'Error', f"Error saving payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                Notification.send_notification(err)

    def update(self):
        self._validate(check_id=True)
        self.save_to_db(update=True)

    def delete(self):
        self._validate(check_id=True)
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            self.query = '''
                DELETE FROM payment WHERE payment_id = ?;
            '''

            try:
                cursor.execute(self.query, (self.payment_id,))
                self.conn.commit()
                self.conn.close()
            except Exception as err:
                log_error_to_file('Payment', 'Error', f"Error deleting payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                log_error_to_file('Payment', 'Error', f'{err}')
                log_to_file('Payment', 'Error', f"Error deleting payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                Notification.send_notification(err)

    @classmethod
    def fetch_one(cls, value, by_name=False, using: str=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        
        try:
            payment_data = fetch_one_entry('payment', cursor, value, by_name)

            if payment_data is None:
                return None
            
            payment_data_obj = {
                'payment_id': payment_data[0],
                'discount': float(payment_data[1]) / 100, # convert from integer
                'tax': float(payment_data[2]) / 100, # convert from integer
                'total_price': float(payment_data[3]) / 100, # convert from integer
                'amount_paid': float(payment_data[4]) / 100, # convert from integer
                'created_at': payment_data[5],
            }

            if payment_data:
                payment = Payment(kwargs=payment_data_obj, using=using)
                return payment
            else:
                return None
        except Exception as err:
            log_to_file('Payment', 'Error', f"Error fetching payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Payment', 'Error', f"Error fetching payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Payment', 'Error', f'{err}')
            return None

    @classmethod
    def fetch_all(cls, using: str=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        payments = []
        try:
            payments_data = fetch_all_entry('payment', cursor)

            if not len(payments_data) > 0:
                return []
            
            for payment_data in payments_data:
                payment_data_obj = {
                    'payment_id': payment_data[0],
                    'discount': float(payment_data[1]) / 100, # convert from integer
                    'tax': float(payment_data[2]) / 100, # convert from integer
                    'total_price': float(payment_data[3]) / 100, # convert from integer
                    'amount_paid': float(payment_data[4]) / 100, # convert from integer
                    'created_at': payment_data[5],
                }

                payment = Payment(kwargs=payment_data_obj, using=using)
                payments.append(payment)
            
            return payments
        except Exception as err:
            log_to_file('Payment', 'Error', f"Error fetching payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Payment', 'Error', f"Error fetching payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Payment', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_payments(cls, value, by_amount=False, by_date=False, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        payments = []
        try:
            if conn:
                cursor = conn.cursor()
               
                if by_date:
                    query = '''
                        SELECT * FROM payment WHERE created_at LIKE ?;
                    '''

                    cursor.execute(query, ('%' + value + '%',))

                if by_amount:
                    query = '''
                        SELECT * FROM payment WHERE total_price = ? OR amount_paid = ?;
                    '''
                    # convert value to kobo
                    value = int(value * 100)
                    cursor.execute(query, (value,value))

                payments_data = cursor.fetchall()

                if not len(payments_data) > 0:
                    return []
                
                for payment_data in payments_data:
                    payment_data_obj = {
                        'payment_id': payment_data[0],
                        'discount': float(payment_data[1]) / 100, # convert from integer
                        'tax': float(payment_data[2]) / 100, # convert from integer
                        'total_price': float(payment_data[3]) / 100, # convert from integer
                        'amount_paid': float(payment_data[4]) / 100, # convert from integer
                        'created_at': payment_data[5],
                    }

                    payment = Payment(kwargs=payment_data_obj, using=using)
                    payments.append(payment)

                return payments
        except Exception as err:
            log_to_file('Payment', 'Error', f"Error fetching payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Payments', 'Error', f"Error fetching payment @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Payments', 'Error', f'{err}')
            return None

    