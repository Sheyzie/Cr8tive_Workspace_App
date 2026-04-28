import time
import inspect
from typing import Self
from datetime import datetime, timedelta
from database.db import InitDB
from database.tables import TABLES_MAP
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from helpers.export_helper import export_helper
from notification.notification import Notification
from helpers.db_helpers import (
    generate_id, 
    insert_to_db, 
    update_in_db, 
    fetch_one_entry, 
    fetch_all_entry
)

import logging

from .plan import Plan
from .client import Client
from .assigned_client import AssignedClient
from .visit import Visit


logger = logging.getLogger(__name__)


class Subscription(InitDB):
    '''
    Subscription model for the subscription table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {
            field_name: value
        }
    '''

    def __init__(self, **kwargs):
        super().__init__()
        self.subscription_id: str = None
        self.plan: Plan = None
        self.client: Client = None
        self.plan_unit: int = 0
        self.expiration_date: str = None
        self.discount = 0
        self.discount_type = 'percent'
        self.vat = 0
        self.status: str = None
        self.payment_status: str = None
        self.created_at: str = None
        self.updated_at: str = None

        self.assigned_users: list[Client] = []

        if kwargs:
            self._get_from_kwargs(**kwargs)
        try:
            self._validate()
        except ValidationError as err:
            self._reset_fields()
            logger.error(str(err.message))
            self.write_error(str(err.message))
            raise err

        self._get_assigned_users

    @property
    def usage(self):
        # {'hourly', 'daily', 'weekly', 'monthly', 'half-year', 'yearly'}
        match self.plan.plan_type:
            case 'hourly':
                return (self.plan.duration / 24) * self.plan_unit
            case 'daily':
                return (self.plan.duration * self.plan_unit) + self.plan.guest_pass
            case 'weekly':
                return ((self.plan.duration * 7) * self.plan_unit) + self.plan.guest_pass
            case 'monthly':
                return ((self.plan.duration * 30) * self.plan_unit) + self.plan.guest_pass
            case 'half-year':
                return ((self.plan.duration * 183) * self.plan_unit) + self.plan.guest_pass
            case 'yearly':
                return ((self.plan.duration * 365) * self.plan_unit) + self.plan.guest_pass
            case _:
                # return daily
                return (self.plan.duration * self.plan_unit) + self.plan.guest_pass
            
    @property
    def subtotal(self):
        return self.plan.price * self.plan_unit
    
    @property
    def discount_amount(self):
        discount =  self.discount
        if self.discount_type == 'percent':
            discount = self.subtotal * (self.discount / 100)
        return discount
    
    @property
    def vat_amount(self):
        return self.subtotal * (self.vat / 100)
    
    @property
    def total_amount(self):
        return float((self.subtotal - self.discount_amount) + self.vat_amount)
    
    @property
    def payments(self):
        from .payment import Payment
        
        payments = Payment.filter_payments(self.subscription_id, by_subscription=True)

        return payments
    
    @property
    def total_paid(self):
        amount = sum(payment.amount for payment in self.payments)
        
        return  amount if amount else 0

    @property
    def balance(self):
        return self.total_amount - self.total_paid
    
    def __str__(self):
        return f'Subscription for {self.plan.plan_name} by {self.client.get_display_name()}'
    
    def _reset_fields(self):
        self.subscription_id: str = None
        self.plan = None
        self.client = None
        self.plan_unit: int = 0
        self.expiration_date: str = None
        self.discount = 0
        self.discount_type = ''
        self.vat = 0
        self.status: str = None
        self.payment_status: str = None
        self.created_at: str = None
        self.updated_at: str = None

    def _get_from_kwargs(self, **kwargs) -> None:
        subscription_id = kwargs.get('subscription_id')
        if subscription_id:
            self.subscription_id = subscription_id

        plan = Plan.fetch_one(plan_id=kwargs.get('plan_id'))
        if plan:
            self.plan = plan

        client = Client.fetch_one(client_id=kwargs.get('client_id'))
        if client:
            self.client = client

        plan_unit = kwargs.get('plan_unit')
        if plan_unit:
            self.plan_unit = plan_unit

        expiration_date = kwargs.get('expiration_date')
        if expiration_date:
            self.expiration_date = expiration_date

        discount = kwargs.get('discount')
        if discount:
            self.discount = float(discount) / 100

        discount_type = kwargs.get('discount_type')
        if discount_type and discount_type in {'percent', 'fixed'}:
            self.discount_type = discount_type

        vat = kwargs.get('vat')
        if vat:
            self.vat = float(vat) / 100

        status = kwargs.get('status', 'booked')
        if status:
            self.status = status

        payment_status = kwargs.get('payment_status')
        if payment_status:
            self.payment_status = payment_status

        assigned_users_id = kwargs.get('assigned_users_id', [])
        assigned_users = []
        for client_id in assigned_users_id:
            client = Client.fetch_one(client_id)
            if client:
                assigned_users.append(client)
        if len(assigned_users) > 0:
            self.assigned_users = assigned_users

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

        updated_at = kwargs.get('updated_at')
        if updated_at:
            self.updated_at = updated_at

    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)
        
        STATUS_TYPE = ['booked', 'running', 'expired', 'exhausted']
        PAYMENT_STATUS_TYPE = ['pending', 'partial', 'paid', 'free']

        if not self.plan:
            raise ValidationError('Plan is not set on subscription')
        if not isinstance(self.plan, Plan):
            raise ValidationError('Plan is not valid on subscription')
        if not self.client:
            raise ValidationError('Client not set on subscription')
        if not isinstance(self.client, Client):
            raise ValidationError('Client is not valid on subscription')
        if not isinstance(self.plan_unit, (int, float)):
            raise ValidationError('Plan unit need to be a number')
        if not self.plan_unit > 0:
            raise ValidationError('Plan unit can not be less than 1')
        if not self.discount:
            raise ValidationError('Payment discount not set on subscription')
        if self.discount < 0:
            raise ValidationError('Payment discount cannot be less than zero')
        if not isinstance(self.discount, (int, float)):
            raise ValidationError('Payment discount cannot be letters')
        if self.discount_type not in {'percent', 'fixed'}:
            raise ValidationError('Payment discount type choices are [percent, fixed]')
        if not self.vat:
            raise ValidationError('Payment vat is required')
        if self.vat < 0:
            raise ValidationError('Payment vat cannot be less than zero')
        if not isinstance(self.vat, (int, float)):
            raise ValidationError('Payment vat cannot be letters')
        if not self.status or self.status not in STATUS_TYPE:
            raise ValidationError(f'Status is required and must include {STATUS_TYPE}')
        if not self.payment_status or self.payment_status not in PAYMENT_STATUS_TYPE:
            raise ValidationError(f'Payment status is required. choice {PAYMENT_STATUS_TYPE}')
        if len(self.assigned_users) > 0 and not all(isinstance(u, Client) for u in self.assigned_users):
                raise ValidationError('Assigned users need to be a list of valid client')
            
        
        if check_id:
            if not self.subscription_id:
                raise ValidationError('Subscription ID is required')
            if not self.expiration_date:
                raise ValidationError('Expiration Date is required')
            
            if not isinstance(self.assigned_users, list):
                raise ValidationError('Assigned users need to be a list of valid client')
            
            if not self._verify_pk():
                raise ValidationError('Subscription ID is not valid')

    def _get_assigned_users(self):
        assigned_clients_id = AssignedClient.filter_sub(sub_id=self.subscription_id)

        assigned_users = []

        if len(assigned_clients_id) > 0:
            for assigned_client_id_tuple in assigned_clients_id:                
                client = Client.fetch_one(client_id=assigned_client_id_tuple[0])
                if client:
                    assigned_users.append(client)
    
        self.assigned_users = assigned_users

    def _set_expiration(self) -> None:
        match(self.plan.plan_type):
            case 'hourly':
                expiration_date = datetime.now() + timedelta(hours=(self.plan.duration * self.plan_unit))
                
            case 'daily':
                expiration_date = datetime.now() + timedelta(days=(self.plan.duration * self.plan_unit))
            case 'weekly':
                expiration_date = datetime.now() + timedelta(weeks=(self.plan.duration * self.plan_unit))
            case 'monthly':
                expiration_date = datetime.now() + timedelta(days=(self.plan.duration * self.plan_unit * 30))
            case 'half-year':
                expiration_date = datetime.now() + timedelta(days=(self.plan.duration * self.plan_unit * 183))
            case 'yearly':
                expiration_date = datetime.now() + timedelta(days=(self.plan.duration * self.plan_unit * 365))
        self.expiration_date = expiration_date.strftime('%Y-%m-%d %H:%M:%S')

    def save(self):
        self._validate()
        self._set_expiration()
        super().save()

    def update(self) -> None:
        self._validate(check_id=True)
        super().update()

    def set_assigned_client(self, client_id) -> None:
        client = Client.fetch_one(client_id=client_id)
        
        if client not in self.assigned_users:
            assigned_client = AssignedClient(subscription_id=self.subscription_id, client_id=client.client_id)
            assigned_client.save()
            self.assigned_users.append(client)

    def remove_assigned_client(self, client_id) -> None:
        if not len(self.assigned_users) > 0:
            return None
        
        for client in self.assigned_users:
            if client.client_id == client_id:
                AssignedClient.delete_user(sub_id=self.subscription_id,client_id=client.client_id)
                self.assigned_users.remove(client)

    def is_user(self, client: Client) -> bool:
        if self.client.client_id == client.client_id:
            return True
        
        for user in self.assigned_users:
            if user.client_id == client.client_id:
                return True
        
        return False
    
    def log_client_to_visit(self, client_id) -> None:
        client = Client.fetch_one(client_id=client_id)
        
        is_user: bool = self.is_user(client)
        
        if not is_user:
            raise Exception(f'User: {client} is not a listed assigned user for this subscription')
        
        if client is None:
            logger.warn('Users does not exist')
            raise Exception(f'User: {client} does not exist please remove user from assigned user')
        
         # check if user is an assigned user
        if not self.is_user(client):
            logger.warn('User is does not have access to this subcription')
        
        # check if subscription is exhausted or expired
        if self.status not in {'booked', 'running'}:
            logger.warn(f'Can not log user in to {self.status} plan')
            raise Exception(f'Can not log user in to {self.status} plan')
        
        is_valid = self.check_expiration()
        if not is_valid:
            logger.warn('Subscription has expired')
            self.status = 'expired'
            self.update()

            raise Exception(f'User: {client} does not exist please remove user from assigned user')

        
        if self.usage == Visit.get_all_sub_visits_count(self.subscription_id):
            self.status = 'exhausted'
            self.update()
            logger.warn('Usage has been exhausted')
            raise Exception('Usage has been exhausted for this subscription')
        
        # TODO: validate if plan is hourly
        visit = Visit(**{'subscription_id': self.subscription_id, 'client_id': client.client_id})
        visit.save()
        
        self.status = 'running'
        self.update()

    def remove_user_visit(self, client_id, date_value: str) -> None:
        # date_value is expecting date in YYYY-MM-DD format
        client = Client.fetch_one(client_id=client_id)
        is_user: bool = self.is_user(client)
        
        if not is_user:
            raise Exception(f'User: {client} is not a listed assigned user for this subscription')
        
        Visit.delete(self.subscription_id, client.client_id, date_value)

    def check_expiration(self):
        from datetime import datetime

        # convert string to datetime
        exp = datetime.strptime(self.expiration_date, "%Y-%m-%d %H:%M:%S")

        # current time
        now = datetime.now()

        return exp > now



