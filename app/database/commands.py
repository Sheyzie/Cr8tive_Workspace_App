import os
from utils.general import get_json
from database.db import get_table_map


class DBService:
    '''
    Helper class to initialize table creation
    '''
    def __init__(self, model):
        self.model = model

        self.field_map = get_table_map(model=model)

    def save_table_to_db(self):
        from database.db import InitDB
        InitDB.model_name = self.model # overwrite model_name to represent new model
        init_db = InitDB() # this initialization will create the tables


class DBCommands:
    '''
    Class for running table related commands
    '''
    def __init__(self, model=None, command=None, validated_args=None, required_args=None, context=None, headers=None, meta=None):
        self.model = model
        self.command = command
        self.validated_args = validated_args
        self.required_args = required_args
        self.context = context
        self.headers = headers
        self.meta = meta
        self.required_contraint = {'is_pk', 'is_unique', 'is_nullable', 'datatype', 'is_date', 'auto_update', 'fk', 'validation'}

        self.table_map = get_table_map()

    def success(self, message='Success', data=None):
        return {
            'success': True,
            'message': message,
            'data': data
        }
    
    def failure(self, message='Failure', error=None):
        return {
            'success': False,
            'message': message,
            'error': error
        }
    
    def process_command(self):  
        return self.process_model_object_function()
            
           
    def process_model_object_function(self):
        ''' Function to run object based command '''

        payload = self.validated_args['payload']
        object_func = getattr(self, self.command.lower())
        try:
            if 'payload' in self.required_args:
                instances = object_func(**payload)
            else:
                instances = object_func()
            return self.success(message=f'{self.command} completed successfully', data=instances)
        except Exception as err:
            print(err)
            return self.failure(message=str(err), error=err)
        
    def is_table(self, table_name):
        return table_name in self.table_map.keys()
        
    def create_model(self, **kwargs):
        ''' Function to write table data to json file '''

        new_table_map = kwargs.get('table_map', {})

        # if self.is_table(self.model):
        #     raise Exception('Table already exist in table map')
        
        field_map = new_table_map.get(self.model, {})

        self.validate_field_map(field_map) # raise exception if not valid

        self.table_map[self.model] = field_map

        formatted_data = get_json(self.table_map, indent=4)

        os.makedirs('database', exist_ok=True)

        file_path = os.path.join('database', 'tables.json')
        with open(file_path, mode='w', encoding='utf-8') as file:
            file.write(formatted_data)


        self.__create_model_class() # create a model_name.py file in models dir
        self.__start_db_service()

    def __create_model_class(self):
        '''
        Function to create a model file in the models dir
        '''
        model_name = self.__format_model_name(self.model)

        fields = self.table_map[self.model]['fields'].keys()

        define_fields = "\n".join(
            f"        self.{field} = None" for field in fields
        )

        get_from_kwargs = "\n".join(
            f"      self.{field} = kwargs.get('field', None)" for field in fields
        )



        content = f'''import time
import inspect
from typing import Self
from database.db import InitDB
from exceptions.exception import ValidationError
from helpers.export_helper import export_helper

import logging

logger = logging.getLogger(__name__)



class {model_name}(InitDB):
    """
    {model_name} model for the {self.model.lower()} table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {{
            field_name: value
        }}
    """
    model_name = '{self.model}'

    def __init__(self, using=None, **kwargs):
        super().__init__()
{define_fields}
        
        if kwargs:
            self._get_from_kwargs(**kwargs)
        try:
            self._validate()
        except ValidationError as err:
            self._reset_fields()
            logger.exception(str(err.message))
            self.write_error(str(err.message))
            raise err

    def __str__(self):
        return self.model_name
    

    def _reset_fields(self):
        """
        Reset all field
        """
{define_fields}

    def _get_from_kwargs(self, **kwargs) -> None:
{get_from_kwargs}


    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)

    def update(self) -> None:
        self._validate(check_id=True)
        super().update()

'''

        file_path = os.path.join('models', f'{self.model}.py')

        if os.path.isfile(file_path):
            # so that we wont overwrite existing model
            return
        
        with open(file_path, mode='w', encoding='utf-8') as file:
            file.write(content)

    def __format_model_name(self, model):
        '''
        Helper method to modify model name for class name
        '''
        import re

        # Replace all delimiters with a space
        model = re.sub(r"[-_]+", " ", model)

        # Capitalize each word and join
        return ''.join(word.title() for word in model.split())
        
    def validate_field_map(self, field_map):
        '''Validator for field map'''

        if field_map == {} or 'fields' not in field_map.keys():
            # expect field attr in field map
            raise Exception('Invalid field map. field is required')
        
        if not isinstance(field_map['fields'], dict) or len(list(field_map['fields'].keys())) == 0:
            # field attr dict must not be empty
            raise Exception('Invalid value for field')
        
        for key in field_map['fields'].keys():
            # field attr dict must have the required contraint keys
            if not set(field_map['fields'][key].keys()) <= self.required_contraint:
               raise Exception('Invalid contraint provide in field') 
                    
    def __start_db_service(self):
        db_service = DBService(self.model)
        db_service.save_table_to_db()

    def get_field_validators(self):
        '''
        Get Field Validators Keys Command
        '''
        from .validation import VALIDATOR_MAP

        data = {}
        for key in VALIDATOR_MAP:
            data[key] = list(VALIDATOR_MAP[key]['validators'].keys())
        return data




def main(**data):
    model = data['validated_args']['model']
    db_command = DBCommands(model=model, **data)
    return db_command.process_command()