import time
import inspect
from typing import Self
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
from .subscription import Subscription
from .client import Client
import logging

logger = logging.getLogger(__name__)


class Payment(InitDB):

    def __init__(self, **kwargs):
        super().__init__()

        self.payment_id = None
        self.client: Client = None
        self.subscription: Subscription = None
        self.amount = 0
        self.created_at = None
        self.updated_at = None
        
        if kwargs:
            self._get_from_kwargs(**kwargs)
        try:
            self._validate()
        except ValidationError as err:
            self._reset_fields()
            logger.exception(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)

    def __str__(self) -> str:
        return f'₦{self.amount} paid for {self.subscription.plan.plan_name}'

    def _reset_fields(self):
        self.payment_id = None
        self.client = None
        self.subscription = None
        self.amount = 0
        self.created_at = None

    def _get_from_kwargs(self, **kwargs) -> None:
        payment_id = kwargs.get('payment_id')
        if payment_id:
            self.payment_id = payment_id

        client = Client.fetch_one(kwargs.get('client_id'))
        if client:
            self.client = client

        subscription = Subscription.fetch_one(kwargs.get('subscription_id'))
        if subscription:
            self.subscription = subscription
        
        amount = kwargs.get('amount')
        if amount:
            self.amount = amount

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

        updated_at = kwargs.get('updated_at')
        if updated_at:
            self.updated_at = updated_at

    def _validate(self, check_id=False) -> None:
        if check_id:
            if not self.payment_id:
                raise ValidationError('Payment not set')
            self._check_payment_id()

        if not self.client:
            raise ValidationError('Client not set payment')
        if not isinstance(self.client, Client):
            raise ValidationError('Client is not valid on payment')
        if not self.subscription:
            raise ValidationError('Subscription not set on payment')
        if not isinstance(self.subscription, Subscription):
            raise ValidationError('Subscription is not valid on payment')
        if not self.amount:
            raise ValidationError('Payment amount is required')
        if not isinstance(self.amount, (int, float)):
            raise ValidationError('Payment amount cannot be letters')
        if self.amount < 0:
            raise ValidationError('Payment amount cannot be less than zero')
        if self.amount > self._get_balance_from_db():
            raise ValidationError('Payment amount cannot be greater than subscription amount')
    
    def get_id(self) -> None:
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            id_string = generate_id('payment', cursor)
            
            if not id_string:
                logger.warn('ID not generated')
                self.stderr.write('\033[31m' + 'ID not generated'+ '\033[0m\n')
                self.stderr.flush()
            
            self.payment_id = id_string
            
            cursor.close()
            self.conn.close()
    
    def _check_payment_id(self):
        '''
        check if id changed
        '''
        payment = Payment.fetch_one(self.payment_id)

        if not payment:
            raise ValidationError('Invalid ID for payment')

    def save_to_db(self, update=False) -> None:
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            updated_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    # convert float to int for precision
                    values = (self.client.client_id, self.subscription.subscription_id, int(self.amount * 100), updated_at, self.payment_id)
                    update_in_db('payment', cursor, values)
                    self.conn.commit()
                    self.conn.close()
                    return

                # convert float to int for precision
                values = (self.payment_id, self.client.client_id, self.subscription.subscription_id, int(self.amount * 100), created_at, updated_at)
                insert_to_db('payment', cursor, values)
                self.conn.commit()
                self.conn.close()
            except ValueError as err:
                logger.warn(str(err))
                self.stderr.write(str(err))
                self.stderr.flush()
                Notification.send_notification(err)

    def update(self) -> None:
        try:
            self._validate(check_id=True)
            self.save_to_db(update=True)
        except ValidationError as err:
            logger.error(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)

    def delete(self) -> None:
        try:
            self._validate(check_id=True)
            self._connect_to_db()
            if self.conn:
                cursor = self.conn.cursor()
                self.query = '''
                    DELETE FROM payment WHERE payment_id = ?;
                '''

            cursor.execute(self.query, (self.payment_id,))
            self.conn.commit()
            self.conn.close()

            # reset fields
            self._reset_fields()
        except ValidationError as err:
            logger.error(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)
        
        except Exception as err:
            logging.error('Error deleting client')
            self.stderr.write(str(err.with_traceback()))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)

    def _get_balance_from_db(self):
        '''
        This function only return the sum of all payments with the 
        subscription_id.

        using this avoids circular class calling when using Subscription.amount_paid
        '''
        conn = self._connect_to_db()
        cursor = conn.cursor()

        query = '''
        SELECT 
            SUM(amount) / 100.0 AS total_amount
        FROM payment
        WHERE subscription_id = ?;
        '''
        try:
            cursor.execute(query, (self.subscription.subscription_id,))
            result = cursor.fetchone()[0]
            return self.subscription.total_amount - (result / 100) if result else self.subscription.total_amount
        except Exception as err:
            logger.warn(str(err))
            self.stderr.write(str(err))
            self.stderr.flush()
            Notification.send_notification(err)
            return self.subscription.total_amount

    @classmethod
    def fetch_one(cls, value, by_name=False) -> Self | None:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        
        try:
            payment_data = fetch_one_entry('payment', cursor, value, by_name)

            if payment_data is None:
                return None
            
            payment_data_obj = {
                'payment_id': payment_data[0],
                'client_id': payment_data[1],
                'subscription_id': payment_data[2],
                'amount': float(payment_data[3]) / 100, # convert from integer
                'created_at': payment_data[4],
                'updated_at': payment_data[5],
            }

            if payment_data:
                payment = Payment(**payment_data_obj)
                return payment
            else:
                return None
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return None

    @classmethod
    def fetch_all(cls) -> list:
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
                    'client_id': payment_data[1],
                    'subscription_id': payment_data[2],
                    'amount': float(payment_data[3]) / 100, # convert from integer
                    'created_at': payment_data[4],
                    'updated_at': payment_data[5],
                }

                payment = Payment(**payment_data_obj)
                payments.append(payment)
            
            return payments
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []

    @classmethod  
    def filter_payments(cls, value, by_subscription=False, by_amount=False, by_date=False) -> list:
        '''
        
        '''
        conn = cls._connect_to_db(cls)
        payments = []
        try:
            if conn:
                cursor = conn.cursor()
               
                if by_date:
                    query = '''
                        SELECT * FROM payment WHERE created_at LIKE ?;
                    '''
                    date_value = value
                    cursor.execute(query, ('%' + date_value + '%',))

                if by_amount:
                    query = '''
                        SELECT * FROM payment WHERE amount >= ? AND amount <= ?;
                    '''
                    # convert value to kobo
                    min_amount = int(value[0] * 100)
                    max_amount = int(value[1] * 100)
                    cursor.execute(query, (min_amount,max_amount))

                if by_subscription:
                    query = '''
                        SELECT * FROM payment WHERE subscription_id = ?;
                    '''
                    # convert value to kobo
                    subscription_id: str = value
                    cursor.execute(query, (subscription_id,))

                payments_data = cursor.fetchall()

                if not len(payments_data) > 0:
                    return []
                
                for payment_data in payments_data:
                    payment_data_obj = {
                        'payment_id': payment_data[0],
                        'client_id': payment_data[1],
                        'subscription_id': payment_data[2],
                        'amount': float(payment_data[3]) / 100, # convert from integer
                        'created_at': payment_data[4],
                        'updated_at': payment_data[5],
                    }

                    payment = Payment(**payment_data_obj)
                    payments.append(payment)

                return payments
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []

    