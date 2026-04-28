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
    '''
    Payment model for the payment table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {
            field_name: value
        }
    '''

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
            self.write_error(str(err.message))
            raise err
        
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

        client = Client.fetch_one(client_id=kwargs.get('client_id'))
        if client:
            self.client = client

        subscription = Subscription.fetch_one(subscription_id=kwargs.get('subscription_id'))
        if subscription:
            self.subscription = subscription
        
        amount = kwargs.get('amount')
        if amount:
            self.amount = float(amount) / 100

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

        updated_at = kwargs.get('updated_at')
        if updated_at:
            self.updated_at = updated_at

    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)

        if check_id:
            if not self.payment_id:
                raise ValidationError('Payment not set')
            if not self._verify_pk():
                raise ValidationError('Payment ID is not valid')

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
   
    def update(self) -> None:
        self._validate(check_id=True)
        super().update()

    def _get_balance_from_db(self):
        '''
        This function only return the sum of all payments with the 
        subscription_id.

        using this avoids circular class calling when using Subscription.amount_paid
        '''


        query = '''
        SELECT 
            SUM(amount) / 100.0 AS total_amount
        FROM payment
        WHERE subscription_id = ?;
        '''

        value = (self.subscription.subscription_id,)

        result = self.custom(query=query, values=value, result_only=True)
        amount = result[0]
        return self.subscription.total_amount - (amount / 100) if amount else self.subscription.total_amount
   
       

