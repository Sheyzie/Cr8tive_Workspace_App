import inspect
import sqlite3
from typing import Self
from logs.utils import log_to_file, log_error_to_file
from exceptions.exception import ValidationError
from helpers.export_helper import export_helper
from helpers.db_helpers import generate_id
from utils.import_file import ImportManager
from configs import db_config
from pathlib import Path
from datetime import datetime
import json
import uuid
import time
import sys
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_table_map(model=None):
    ''' Helper function to get table map for all model or specific model if model is set'''
    
    os.makedirs('database', exist_ok=True)

    file_path = os.path.join('database', 'tables.json')
    data = {}
    with open(file_path, mode='r') as file:
        data = json.load(file)
    if not model:
        return data
    
    if data == {}:
        return data
    
    return data.get(model, {})


class DB:
    '''
    The base class responsible for database connection and table 
    creation.
    - Tables are created from TABLE_MAP imported from database.tables.
    - TABLE_MAP is a dictionary mapping all the required details needed
        to create a table in the database.
        - TABLE_MAP follow the heirarchy: 
            table_name -> fields -> column_name -> field_contraint

        TABLES_MAP = {
            'user': {
                'fields': {
                    'user_id': {
                        'is_pk': True,
                        'is_unique': True,
                        'is_nullable': False,
                        'datatype': UUID
                    },
                    'full_name': {
                        'is_pk': False,
                        'is_unique': False,
                        'is_nullable': True,
                        'datatype': str,
                    },
                    'role_id': {
                        'is_pk': False,
                        'is_unique': False,
                        'is_nullable': True,
                        'datatype': UUID,
                        'fk': {
                            'to': 'role',
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
    '''
    default_field_keys = {'is_pk', 'is_unique', 'fk', 'is_nullable', 'to', 'is_date', 'auto_update', 'datatype', 'validation'}
    table_map = get_table_map() 
    allow_print = False
    show_sql = False
    stdout = sys.stdout
    stderr = sys.stderr
    _db = None

    def __init__(self, using):

        self.allow_print = False
        self.show_sql = False

        try:
            self.field_map = self._get_field_map()
        except TypeError:
            self.field_map = self._get_field_map(self)
        
        conn = None
        logger.info('Initializing database connection for {self.model_name}...')
        self.write(f'Initializing database connection for {self.model_name}...')
        
        if not using:
            logger.warn(f"No Database provided. Ensure DB config is set @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            self.write_error('No Database provided. Ensure DB config is set')
            exit(1)
        try:
            self._db = using
            conn = sqlite3.connect(Path(self._db))
            conn.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f'Database connection established to {self._db}')
            self.write(f'Database connection established to {self._db}\n')

            conn.close()

            self._init_database_tables()
        except Exception as err:
            conn.close()
            logger.exception(f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.write_error(f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.write_error(str(err))
            self.stderr.flush()

            raise err
                
    def _connect_to_db(self):
        '''
        handles reconnection to database
        '''

        if self._db is None:
            DB.set_db_name()
        try:
            if self.allow_print:
                self.write('\nInitializing database connection...\n')
            self.conn = sqlite3.connect(Path(self._db))

            # access column by name (like a dictionary)
            # self.conn.row_factory = sqlite3.Row

            self.conn.execute("PRAGMA foreign_keys = ON")
            # logger.info('Database connection established')

            if self.allow_print:
                self.write('Database connection established\n')

            return self.conn
        except Exception as err:
            logger.exception(f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.write_error(f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.write_error(str(err))
            self.conn.close()
            raise err

    @classmethod    
    def write_error(self, error: str):
        self.stdout.write(f'\033[31m{error}\033[0m\n')
        self.stdout.flush()

    @classmethod
    def write(self, text):
        self.stdout.write(f'{text}\n')
        self.stdout.flush()

    @classmethod
    def set_db_name(cls):
        '''
        Change database name depending on if environment is test environment
        '''
        is_test_environ = os.getenv('CURRENT_WORKING_DB_ENVIRON', '').lower() == 'test' 
        using = db_config.TEST_DB_NAME
        if not is_test_environ:
            using = db_config.DB_NAME

        if not using:
            logger.warn(f"Database name not found\n")
            cls.stderr.write(f"Database name not set found\n")
            cls.stderr.flush()
            exit(0)

        cls._db = using
        return using

    def _set_table_name(self):
        '''
        Set the model to be used as table name.
            - model_name is not declared in the Model class, the model 
            name will be used as the table name
        '''
        # get table name from model
        model_name = getattr(self, 'model_name', None)
        if not model_name:
            try:
                model_name = self.__name__ # use model name as table name
            except AttributeError:
                model_name = self.__class__.__name__
        
        setattr(self, 'model_name', model_name.lower())
    
    def _get_field_map(self):
        '''
        Returns the field of the current intance of the model 
        configured in TABLE_NAME
        '''
        try:
            self._set_table_name()
        except TypeError:
            self._set_table_name(self)

        field_map = self.table_map.get(self.model_name, None)
        if field_map is None:
            logger.exception(f'No table match the name {self.model_name} ensure table is on TABLE_MAP')
            raise Exception(f'No table match the name {self.model_name} ensure table is on TABLE_MAP')
        return field_map.get('fields')

    def _init_database_tables(self):
        '''
        Gets all tables in the TABLE_MAP and create the tables in the
        database if tables do not exist
        '''

        tables = self.table_map.keys()

        for table_name in tables:
            self.create_tables(table_name=table_name)

    def create_tables(self, table_name):
        '''
        Handles table creation if table does not exist
        '''
        exists = self._check_if_table_exist(table_name)
        
        if exists:
            if self.allow_print:
                self.write(f'\n{table_name} table exist\n')
            return

        table_detail = self._get_table_detail(table_name=table_name)
        
        table_field_map = self.table_map.get(table_name).get('fields')

        # get fk map from detail
        fk_field_map = table_detail.get('fk_field_map', {})
        if fk_field_map != {}:
            # create fk table if not exist
            for field, contraint in fk_field_map.items():
                fk_model = contraint['to']
                exists = self._check_if_table_exist(fk_model)
                if not exists:
                    self.create_tables(fk_model)
        
        
        # generate sql
        # CREATE TABLE IF NOT EXISTS payment (
        #         payment_id TEXT PRIMARY KEY  , 
        #         client_id TEXT  NOT NULL , 
        #         subscription_id TEXT  NOT NULL , 
        #         amount INTEGER  NOT NULL , 
        #         created_at TEXT  NOT NULL , 
        #         updated_at TEXT  NOT NULL
        #         FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE ON UPDATE NO ACTION,
        #         FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id) ON DELETE CASCADE ON UPDATE NO ACTION);
    
        query = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                {',\n\t\t'.join([
                f'{field} {( 
                    # set datatype,  
                    self._get_datatype(table_detail.get('datatype').get(field))
                    )}{(
                        # set pk
                        ' PRIMARY KEY' if table_detail.get('pk_field') == field else ''

                    )}{(
                        # set not null,
                        ' NOT NULL' if field in table_detail.get('not_null_fields', []) else ''
                        )}{(
                        # set unique
                        ' UNIQUE' if field in table_detail.get('unique_fields', []) else ''
                        # loop thru keys,
                    )}' for field in table_field_map.keys()
            ])}{(
                ''.join((
                    # add foreign keys
                    f',\n\t\tFOREIGN KEY ({field}) REFERENCES {(
                        table_detail.get('fk_field_map', {}).get(field).get('to')
                        )}({field}) ON DELETE {(
                            table_detail.get('fk_field_map', {}).get(field, None).get('on_delete', '').upper()
                                                )} ON UPDATE {(
                                                    table_detail.get('fk_field_map', {}).get(field).get('on_update', '').upper()
                                                    )}' for field in table_field_map.keys() if table_detail.get('fk_field_map', {}).get(field, None) is not None
                ))
            )});
        '''
        
        if self.show_sql:
            self.write(query)

        self._connect_to_db()
        if self.conn:
            if self.allow_print:
                self.write(f'Creating database table {table_name}...')

            cursor = self.conn.cursor()
            try:
                cursor.execute(query)
                self.conn.commit()
            except Exception as err:
                self.conn.close()
                logger.exception(f"Error creating {table_name} table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                self.write_error(f"Error creating {table_name} table")
                self.write(str(err))
                raise err

            self.conn.close()

    def _get_datatype(self, obj):
        '''
        Gets the datatype value of a field and return the 
        required datatype needed for sql querry
        '''

        if obj == 'str':
            return 'TEXT'
        elif obj == 'int':
            return 'INTEGER'
        elif obj == 'dict':
            return 'TEXT'
        elif obj == 'UUID':
            return 'TEXT'
        elif obj == 'datetime':
            return 'TEXT'

    def _get_table_detail(self, table_name):
        '''
        Summarize the TABLE_MAP into a dictionary to be used for generating
        the necessary query for table creation
        {
            'pk_field': 'payment_id', 
            'datatype': {
                'payment_id': <class 'uuid.UUID'>, 
                'client_id': <class 'uuid.UUID'>, 
                'subscription_id': <class 'uuid.UUID'>, 
                'amount': <class 'int'>, 
                'created_at': <class 'datetime.datetime'>, 
                'updated_at': <class 'datetime.datetime'>
                }, 
            'fk_field_map': {
                'client_id': {
                    'on_delete': 'cascade', 
                    'on_update': 'no action',  
                    'to': 'client'
                }, 
                'subscription_id': {
                    'on_delete': 'cascade', 
                    'on_update': 'no action', 
                    'to': 'subscription'
                }
            }, 
            'not_null_fields': ['client_id', 'subscription_id', 'amount', 'created_at', 'updated_at'], 
            'unique_fields': []
        }

        '''

        PK_FEILD = None
        FK_FEILDS_MAP = {}
        UNIQUE_FIELDS = []
        NOT_NULL_FIELDS = []
        DATATYPE_MAP = {}

        table_field = self.table_map.get(table_name, None)
   
        if table_field is None:
            raise ValidationError(f"Invalid table name '{table_name}'. ensure table is in TABLE_MAP")

        table_field_map = table_field.get('fields', None)
        if table_field_map is None:
            raise ValidationError(f"Field not present in TABLE_MAP for {table_name}")
        
        for key in table_field_map.keys():
            field = table_field_map.get(key, None)
            if field is None:
                raise ValidationError(f"Invalid field '{key}' provided for {table_name}")
            
            if not set(field.keys()) <= set(self.default_field_keys):
                raise ValidationError(f'Unknown keys {set(field.keys()) - set(self.default_field_keys)} provided')
            
            is_pk = field.get('is_pk', False)
            if is_pk:
                # if primary key value was earlier set
                if PK_FEILD:
                    raise ValidationError(f'Primary key field already set to {PK_FEILD}')
                
                # set pk field
                PK_FEILD = key

            datatype = field.get('datatype', None)
            if not datatype:
                raise ValidationError(f'Datatype is required for creating a field in a table')
            
            # if not isinstance(datatype, (str, int, datetime, uuid.UUID, dict)):
            if not datatype in ('str', 'int', 'datetime', 'UUID', 'dict'):
                raise ValidationError(f'Datatype of type {datatype} is not valid')
            
            DATATYPE_MAP[key] = datatype
            
            is_unique = field.get('is_unique', False)
            if is_unique:
                if key != PK_FEILD:
                    UNIQUE_FIELDS.append(key)

            is_nullable = field.get('is_nullable', False)
            if is_nullable:
                if key == PK_FEILD:
                    raise ValidationError(f'Primary key field is a non nullable field {key}')
            else:
                if key != PK_FEILD:
                    NOT_NULL_FIELDS.append(key)
                
            fk = field.get('fk', None)
            if fk is not None:
                reference_model = fk.get('to', None)
                if reference_model not in self.table_map.keys():
                    raise ValidationError(f'Invalid model {reference_model} for {key}')
                
                contraint = {}
                on_delete = fk.get('on_delete', None)
                on_update = fk.get('on_update', None)

                contraint['on_delete'] = on_delete if on_delete is not None else 'no action'
                contraint['on_update'] = on_update if on_update is not None else 'no action'
                contraint['to'] = reference_model
                
                # map constraint to key
                FK_FEILDS_MAP[key] = contraint
        
        table_detail = {
            'pk_field': PK_FEILD,
            'datatype': DATATYPE_MAP,
            'fk_field_map': FK_FEILDS_MAP,
            'not_null_fields': NOT_NULL_FIELDS,
            'unique_fields': UNIQUE_FIELDS
        }

        return table_detail
        
    def _check_if_table_exist(self, table_name: str):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            try:
                query = '''
                    SELECT name 
                    FROM sqlite_master 
                    WHERE type='table' AND name=?
                '''
                cursor.execute(query, (table_name,))

                if self.show_sql:
                    self.write(query)
                result = cursor.fetchone()
                return result

            except Exception as err:
                self.stderr.write(f"Error creating client table @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
                self.stderr.write(str(err))
                self.stderr.flush()

    def drop_db(self):
        self.write(f'Dropping database {self._db}\n')
        logger.info(f'Dropping database {self._db}\n')
        db_file = Path(self._db)
        
        if db_file.exists():
            db_file.unlink()
            self.write(f'Dropped {self._db} database successfully\n')
            logger.info(f'Dropped {self._db} database successfully\n')

        else:
            self.write(f'Database {self._db} not found\n')
            logger.error(f'Database {self._db} not found\n')
            exit(1)


class InitDB(DB):
    '''
    DB subclass responsible for CRUD operations and ORM for the 
    current instance of a model
    '''
    
    def __init__(self):
        is_test_environ = os.getenv('CURRENT_WORKING_DB_ENVIRON', '').lower() == 'test' 
        using = db_config.TEST_DB_NAME
        if not is_test_environ:
            using = db_config.DB_NAME

        super().__init__(using)

    @property
    def data(self):
        return self._get_data()
    
    
    def _validate(self, check_id=False) -> None:
        ''' Validate Fields Based on validation set '''
        
        from database.validation import VALIDATOR_MAP

        
        fields = self.table_map[self.model_name]['fields']

        for field, config in fields.items():
            validations = config.get('validation', [])
            datatype = config.get('datatype')
            is_pk = config.get('is_pk', False)

            if is_pk and not check_id:
                continue

            for validation in validations:
                validator = VALIDATOR_MAP.get(datatype, {}).get('validators', {}).get(validation['name'])

                if not validator:
                    raise ValidationError(f"Validator {validation['name']} not found")

                value = getattr(self, field, None)
                result = validator(value, validation.get('value'))

                if result != validation.get('exp_value'):
                    raise ValidationError(f"{field} failed {validation['name']}")
    
    def _get_pk_field(self):
        '''
        returns the fields contraint for the primary key 
        '''
        try:
            field_map = self._get_field_map()
        except TypeError:
            field_map = self._get_field_map(self)

        model = self.model_name
        model_fields = list(field_map.keys())

        data = {}

        for key in model_fields:
            field_obj = field_map.get(key, {})
            is_pk = field_obj.get('is_pk', False)
            
            if is_pk:
                data = {
                    key: field_obj
                }
                break
        return data   
    
    def _verify_pk(self):
        '''
        check if id changed
        '''
        pk_key = list(self._get_pk_field().keys())[0]
        kwargs = {
            pk_key: getattr(self, pk_key)
        }

        instance = self.fetch_one(**kwargs)
        return instance is not None

    def _get_data(self, is_new=False):
        '''
        A serializer for the current models instance
        '''
        try:
            field_map = self._get_field_map()
        except TypeError:
            field_map = self._get_field_map(self)

        model = self.model_name
        model_fields = list(field_map.keys())

        data = {}
        
        for field in model_fields: # map thru each field(column name) from TABLE_MAP
            # format field to change fk(subscription_id becomes subscription)
            formatted_field = field if field[-3:] != '_id' or field == f'{model.lower()}_id' else field[:-3]

            if hasattr(self, formatted_field):
                value = getattr(self, formatted_field)
                
                if value is not None and not isinstance(value, InitDB):
                    data[field] = value

                if isinstance(value, InitDB):
                    fk_value = getattr(value, field, None)
                    if fk_value is not None:
                        data[field] = fk_value

            # check if field is private field
            if hasattr(self, f'_{formatted_field}'):
                value = getattr(self, f'_{formatted_field}')
                if value is not None and not isinstance(value, InitDB):
                    data[field] = value

                if isinstance(value, InitDB):
                    fk_value = getattr(value, field, None)
                    if fk_value is not None:
                        data[field] = fk_value

            if field[-3:] == '_id':
                value = getattr(self, field, None)
                if value is not None:
                    data[field] = value

        # validate fields
        is_valid = self._is_valid_data(data, is_new=is_new) 
        if is_valid:
            return data
        return None

    def _is_valid_data(self, data, is_new=False):
        '''
        Check if model data meet the criteria of the field contraint
        '''
        try:
            field_map = self._get_field_map()
        except TypeError:
            field_map = self._get_field_map(self)

        model = self.model_name
        model_fields = list(field_map.keys())

        pk_value = None
        unique_values = []

        for field in model_fields:
            field_obj = field_map.get(field, {})
            is_pk = field_obj.get('is_pk', False)
            is_unique = field_obj.get('is_unique', False)
            is_nullable = field_obj.get('is_nullable', True)
            fk = field_obj.get('fk', None)

            value = data.get(field, None)

            # check pk for existing record
            if not is_new:
                if is_pk:
                    # if primary key value was earlier set
                    if pk_value:
                        raise ValidationError(f'Primary key value already set to {pk_value}')
                    
                    # get pk value
                    pk_value = value
                    if not pk_value:
                        raise ValidationError(f'Primary key value is not nullable for field {field}')
                    
                    # check if pk value is unique
                    if pk_value in unique_values:
                        raise ValidationError(f'Primary key: {pk_value}  has to be unique')
                    
                    unique_values.append(pk_value)
        
            if is_unique:
                # get unique value
                unique_value = value
                if not unique_value:
                    if not is_pk and not is_new:
                        raise ValidationError(f'Value is required for field with unique contraint {field}')
                
                # check if pk value is unique
                if unique_value in unique_values:
                    # pk field field will vallidate it's own uniqueness above
                    if not is_pk:
                        raise ValidationError(f'UNIQUE CONSTRAINT: {unique_value} already exist in table')
                
                if is_new and not is_pk: # inform if data is new entry and field is not pk field
                    self._check_unique_value_in_db(field, value)
                
                unique_values.append(unique_value)
                

            if not is_nullable:
                if not value:
                    if not is_pk and not is_new:
                        raise ValidationError(f'Value is required for non nullable field {field}')

            if fk is not None:
                reference_model = fk.get('to', None)
                if reference_model not in self.table_map.keys():
                    raise ValidationError(f'Invalid model {reference_model} for {field}')

            return True 
                
    def _get_id(self) -> str | None:
        '''
        Create UUID for pk field
        '''
        try:
            self._set_table_name()
        except TypeError:
            self._set_table_name(self)

        self._connect_to_db()
        if self.conn:
            model = self.model_name
            id_exist = True
            id_string = ""

            cursor = self.conn.cursor()

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
                    logging.exception(str(err))
                    sys.stderr.write(f'\n{err}\n')
                    sys.stderr.flush()
                    return None
            return id_string

    def _check_unique_value_in_db(self, field, value):
        '''
        Check if a unique value is present in db before save
        '''
        model = self.model_name

        query = f'SELECT * FROM {model} WHERE {field} = ?;'

        self._connect_to_db()
        
        if self.conn:
            cursor = self.conn.cursor()

            result = None
            
            try:
                cursor.execute(query, (value,))
                result = cursor.fetchone()
                self.conn.close()
            except Exception as err:
                logger.exception('Error saving client')
                self.stderr.write(str(err))
                self.stderr.flush()

                self.conn.close()
                raise err
            
            if result is not None:
                raise ValidationError(f'Unique field {field} already has the value {value}')

    def __save_to_db(self, **kwargs) -> None:
        '''
        Save the data on the current instace of the model in 
        the database
        '''
        try:
            field_map = self._get_field_map()
        except TypeError:
            field_map = self._get_field_map(self)

        model = self.model_name

        model_fields = list(field_map.keys())
        update = kwargs.get('update', False)

        if update and not isinstance(update, bool):
            raise Exception(f'Invalid type for update got {type(update)} but expected bool')
                
        validated_data = self._get_data(is_new=True)

        pk_key = ''
        pk_value = ''
        query = ''
        values = tuple()
        # handle date
        for key in model_fields:
            field_obj = field_map.get(key, {})
            is_pk = field_obj.get('is_pk', False)
            is_date = field_obj.get('is_date', False)
            auto_update = field_obj.get('auto_update', 'never')

            value = validated_data.get(key, None)
            
            # get pk field key and value
            if is_pk:
                pk_key = key
                pk_value = value

            # check if date field require auto update
            if is_date:
                match auto_update:
                    case 'never':
                        validated_data[key] = value
                    case 'save':
                        validated_data.pop(key, None)
                        if not update:
                            validated_data[key] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    case 'update':
                        validated_data[key] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        if not update:
            # get primary key string
            uuid_string = self._get_id()

            # add key to object
            data = {
                pk_key: uuid_string,
                **validated_data
            }

            # if model has no primary key
            if not pk_key:
                data = {
                    f'{model.lower()}_id': uuid_string,
                    **validated_data
                }
            
            # set id to object
            setattr(self, pk_key, uuid_string)

            # please ignore the tab sapce \t: it is used to make the query readable on terminal
            query = f'''
                    INSERT INTO {model.lower()}({',\n\t\t\t'.join([key for key in data.keys()])})
                    VALUES ({', '.join(['?' for key in data.keys()])});
            '''
            values = tuple(data.values())

        if update:
            pk_value = validated_data.pop(pk_key, None)
            data = {
                **validated_data,
                pk_key: pk_value
            }

            # please ignore the tab sapce \t: it is used to make the query readable on terminal
            query = f'''
                    UPDATE {model.lower()} 
                    SET {', '.join([f'{key} = ?' for key in data.keys() if key != pk_key])}
                    WHERE {f'{pk_key} = ?'};
            '''
            values = tuple(data.values())

        if self.show_sql:
            self.write(query)

        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()

            try:
                cursor.execute(query,values)
                self.conn.commit()
                self.conn.close()

            except Exception as err:
                logger.exception('Error saving client')
                self.stderr.write(str(err))
                self.stderr.flush()
                self.conn.close()
                raise err

    def save(self):
        self.__save_to_db()

    def update(self):
        self.__save_to_db(update=True)
 
    def delete(self) -> None:
        try:
            field_map = self._get_field_map()
        except TypeError:
            field_map = self._get_field_map(self)

        model = self.model_name
        model_fields = list(field_map.keys())

        pk_key = ''
        for key in model_fields:
            field_obj = field_map.get(key, {})
            is_pk = field_obj.get('is_pk', False)


            if is_pk:
                pk_key = key

        try:
            self._connect_to_db()
            if self.conn:
                cursor = self.conn.cursor()
                query = f'''
                    DELETE FROM {model.lower()} WHERE {pk_key} = ?;
            '''
            if self.show_sql:
                self.write(query)

            cursor.execute(query, (getattr(self, pk_key),))
            self.conn.commit()
            self.conn.close()

            # reset fields back
            self._reset_fields()
        except ValidationError as err:
            logger.exception(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            self.conn.close()
            raise err
        except Exception as err:
            logging.exception(f'Error deleting {model}')
            self.stderr.write(str(err))
            self.stderr.flush()
            self.conn.close()
            raise err

    @classmethod
    def fetch_one(cls, **kwargs) -> Self | None:
        '''
        Get one item from model table. Return None if no item is found
        '''
        try:
            field_map = cls._get_field_map()
        except TypeError:
            field_map = cls._get_field_map(cls)

        model = cls.model_name
        model_fields = field_map.keys()

        if not field_map:
            raise Exception(f'Field map not found for {model} model')
        
        if not set(kwargs.keys()) <= set(model_fields):
            raise Exception(f'Invalid field provided for {model} model')
        
        # get model name

        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        query = f'''
            SELECT * FROM {model.lower()}
            WHERE {' AND '.join([f'{key} = ?' for key in kwargs.keys()])};
        '''

        if cls.show_sql:
            cls.write(query)

        values = tuple(kwargs.values())

        try:
            cursor.execute(query, values)
            result = cursor.fetchone()

            cursor.close()
            conn.close()
            if result is None:
                return None
            
            data = {}   
            for i in range(len(model_fields)):
                data[list(model_fields)[i]] = result[i]

            instance = cls(**data)
            return instance
        except Exception as err:
            cursor.close()
            conn.close()
            logger.exception(f'Error fetching {model}')
            cls.stderr.write(str(err))
            cls.stderr.flush()

            raise err

    @classmethod
    def fetch_all(cls, **kwargs) -> Self | None:
        '''
        Get all items from the model.
        '''
        try:
            field_map = cls._get_field_map()
        except TypeError:
            field_map = cls._get_field_map(cls)

        model = cls.model_name
        model_fields = field_map.keys()
        col_names = kwargs.get('col_names', False)
        page = kwargs.get('page', 1) # default page
        page_size = kwargs.get('page_size', 100) # default pagination

        if not field_map:
            raise Exception(f'Field map not found on {model} model')
        
        if col_names and not isinstance(col_names, bool):
            raise Exception(f'Invalid type for col_names got {type(col_names)} but expected bool')
        
        if page and not isinstance(page, int):
            raise Exception(f'Invalid type for page got {type(page)} but expected int')
        
        if page_size and not isinstance(page_size, int):
            raise Exception(f'Invalid type for page_size got {type(page_size)} but expected int')
        
        OFFSET = (page - 1) * page_size
 
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        query = f'''
            SELECT * FROM {model.lower()}
            LIMIT {page_size}
            OFFSET {OFFSET};
        '''

        if cls.show_sql:
            cls.write(query)

        try:
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not len(result) > 0:
                return []
            
            # only exports will set col_name to true so no need to create client obj
            if col_names:
                # Get column names
                column_names = [description[0] for description in cursor.description]

                return (result, column_names)

            instance_list = []
            for data_tuple in result:
                data = {}
                for i in range(len(model_fields)):
                    data[list(model_fields)[i]] = data_tuple[i]

                instance = cls(**data)
                instance_list.append(instance)
            
            return instance_list
        except Exception as err:
            cursor.close()
            conn.close()
            logger.exception(f'Error fetching {model}')
            cls.stderr.write(str(err))
            cls.stderr.flush()

            raise err

    @classmethod  
    def filter(cls, **kwargs) -> list:
        '''
        Filter model table based on the values of the model fields
        '''
        try:
            field_map = cls._get_field_map()
        except TypeError:
            field_map = cls._get_field_map(cls)

        model = cls.model_name
        model_fields = field_map.keys()
        date_like_keys = []

        # get date like keys for wild cards
        for key in model_fields:
            field_obj = field_map.get(key, {})
            is_date = field_obj.get('is_date', False)
            
            if is_date:
                date_like_keys.append(key)

        page = kwargs.pop('page', 1) # default page
        page_size = kwargs.pop('page_size', 100) # default pagination

        if not field_map:
            raise Exception(f'Field map not found on {model} model')
        
        if not set(kwargs.keys()) <= set(model_fields):
            raise Exception(f'Invalid field provided {model} model')
        
        if page and not isinstance(page, int):
            raise Exception(f'Invalid type for page got {type(page)} but expected int')
        
        if page_size and not isinstance(page_size, int):
            raise Exception(f'Invalid type for page_size got {type(page_size)} but expected int')
        
        OFFSET = (page - 1) * page_size
        
        # get model name

        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        # add wild card to date like values
        for key, value in kwargs.items():
            if key in date_like_keys:
                kwargs[key] = f'%{value}%'

        query = f'''
            SELECT * FROM {model.lower()}
            WHERE {' AND '.join([f'{key} = ?' if key not in date_like_keys else f'{key} LIKE ?' for key in kwargs.keys()])}
            LIMIT {page_size}
            OFFSET {OFFSET};
        '''

        values = tuple(kwargs.values())

        if cls.show_sql:
            cls.write(query)

        try:
            cursor.execute(query, values)
            result = cursor.fetchall()
            cursor.close()
            conn.close()

            if not len(result) > 0:
                return []
            
            instance_list = []
            for data_tuple in result:
                data = {}
                for i in range(len(model_fields)):
                    data[list(model_fields)[i]] = data_tuple[i]

                instance = cls(**data)
                instance_list.append(instance)
            
            return instance_list
        except Exception as err:
            conn.close()
            logger.exception(f'Error fetching {model}')
            cls.stderr.write(str(err))
            cls.stderr.flush()

            raise err
    
    @classmethod
    def custom(cls, **kwargs) -> Self | None:
        '''
        Send send custom sql query to the database
        '''
        try:
            field_map = cls._get_field_map()
        except TypeError:
            field_map = cls._get_field_map(cls)

        model = cls.model_name
        model_fields = field_map.keys()
        query = kwargs.get('query', None)
        values = kwargs.get('values', [])
        many = kwargs.get('many', False)
        col_names = kwargs.get('col_names', False)
        values_only = kwargs.get('values_only', False)
        result_only = kwargs.get('result_only', False)
        
        if not field_map:
            raise Exception(f'Field map not found on {model} model')
        
        if query and not isinstance(query, str):
            raise Exception(f'Invalid type for query got {type(query)} but expected string')
        
        if len(values) > 0 and not isinstance(values, tuple):
            raise Exception(f'Invalid type for values got {type(values)} but expected tuple')
        
        if many and not isinstance(many, bool):
            raise Exception(f'Invalid type for many got {type(many)} but expected bool')
        
        if col_names and not isinstance(col_names, bool):
            raise Exception(f'Invalid type for col_names got {type(col_names)} but expected bool')
        
        if values_only and not isinstance(values_only, bool):
            raise Exception(f'Invalid type for values_only got {type(values_only)} but expected bool')
        
        if result_only and not isinstance(result_only, bool):
            raise Exception(f'Invalid type for result_only got {type(result_only)} but expected bool')
 
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        if cls.show_sql:
            cls.write(query)

        try:
            if len(values) == 0:
                cursor.execute(query)
            else:
                cursor.execute(query, values)

            if not many:
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                if result is None:
                    conn.close()
                    return None
                
                if result_only:
                    return result
                
                data = {}   
                for i in range(len(model_fields)):
                    data[list(model_fields)[i]] = result[i]

                if values_only:
                    return data

                instance = cls(**data)

                return instance
            else:

                result = cursor.fetchall()
                cursor.close()
                conn.close()

                if not len(result) > 0:
                    return []
                
                if result_only:
                    return result
                
                # only exports will set col_name to true so no need to create client obj
                if col_names:
                    # Get column names
                    column_names = [description[0] for description in cursor.description]

                    return (result, column_names)

                instance_list = []
                for data_tuple in result:
                    data = {}
                    for i in range(len(model_fields)):
                        data[list(model_fields)[i]] = data_tuple[i]

                    instance = cls(**data)
                    instance_list.append(instance)

                return instance_list
        except Exception as err:
            conn.close()
            logger.exception(f'Error fetching {model}')
            cls.stderr.write(str(err))
            cls.stderr.flush()

            raise err

    @classmethod
    def import_model(cls, filepath, file_type, has_header):
        '''
        Import in to the model from csv, xls, pdf
        '''
        try:
            field_map = cls._get_field_map()
        except TypeError:
            field_map = cls._get_field_map(cls)

        logger.info(f'Importing {cls.model_name} from {file_type}...')
        cls.write(f'Importing {cls.model_name} from {file_type}...')

        model = cls.model_name
        model_fields = list(field_map.keys())

        # remove and id, created_at and updated_at from list
        model_fields.remove(f'{model.lower()}_id')
        model_fields.remove('created_at')
        model_fields.remove('updated_at')

        if not field_map:
            raise Exception(f'Field map not found on {model} model')
 
        manager = ImportManager(file_path=filepath, file_type=file_type, has_header=has_header)
        
        instance_data = []
        instances = []
        failed_imports = []

        if file_type.lower() == '.csv':
            for data_tuple in manager.import_from_csv():
                data = {}
                if not has_header:
                    for i in range(len(model_fields)):
                        data[model_fields[i]] = data_tuple[i]

                else:
                    data = data_tuple

                instance_data.append(data)

        elif file_type.lower() in {'.xls', '.xlsx'}:
            for data_tuple in manager.import_from_excel():
                data = {}
                for i in range(len(model_fields)):
                    data[list(model_fields)[i]] = data_tuple[i]

                instance_data.append(data)

        else:
            for data_tuple in manager.import_from_pdf():
                data = {}
                for i in range(len(model_fields)):
                    data[list(model_fields)[i]] = data_tuple[i]

                instance_data.append(data)

        for data in instance_data:
            try:
                instance = cls(**data)
                instance.save()
                instances.append(instance)
            except Exception as err:
                failed_imports.append((data, {'reason': str(err)}))
                continue
            
        for i, failed_import in enumerate(failed_imports):
            cls.stdout.write(f'{i + 1} failed: {failed_import[1]['reason']}')
            cls.stdout.flush()
        logger.info(f'({len(instances)}/{len(instances) + len(failed_imports)}) {cls.model_name} imported successfully')
        cls.write(f'({len(instances)}/{len(instances) + len(failed_imports)}) {cls.model_name} imported successfully\n')

    @classmethod
    def export_model(cls, file_type, path):
        '''
        Export into csv, xls, pdf
        '''

        instance_data, column_names = cls.fetch_all(col_names=True)

        column_names = column_names if column_names else None

        # remove unnecessary data like ID 
        formated_data = []

        for data in instance_data:
            data = list(data)
            data.pop(0)
            formated_data.append(data)
        
        column_names.pop(0)

        formatted_header = []
        
        for header in column_names:
            if file_type == '.pdf':
                header = header.replace('_', ' ').upper()
            formatted_header.append(header)
            

        data = {
            'entries': formated_data,
            'headers': formatted_header
        }

        export_helper(cls, file_type, path, data=data, name='clients_export')
        print('Export complete')
  

