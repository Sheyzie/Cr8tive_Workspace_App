import os
from utils.general import get_json
from database.fields import get_contraint_keys_by_field_name, get_field_from_datatype
from database.db import get_table_map, format_model_name


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
        # self.required_contraint = get_contraint_keys()

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
        return os.path.isfile(os.path.join('models', f'{table_name}.py'))
        # return table_name in self.table_map.keys()
        
    def create_model(self, **kwargs):
        ''' Function to write table data to json file '''

        new_table_map = kwargs.get('table_map', {})

        if self.is_table(self.model):
            raise Exception(f'Model {self.model} already exist')
        
        field_map = new_table_map.get(self.model, {})
        
        self.validate_field_map(field_map) # raise exception if not valid

        self.table_map[self.model] = field_map

        formatted_data = get_json(self.table_map, indent=4)

        os.makedirs('database', exist_ok=True)
        
        # file_path = os.path.join('database', 'tables.json')
        # with open(file_path, mode='w', encoding='utf-8') as file:
        #     file.write(formatted_data)

        self.__create_model_class(field_map['fields']) # create a model_name.py file in models dir
        self.__start_db_service()

    def create_bulk_models(self, **kwargs):
        table_map_list = kwargs.get('table_maps')
        data = {}
        for table_map in table_map_list:
            self.model = list(table_map.keys())[0]
            data['table_map'] = table_map
            self.create_model(**data)

        return 'Model created successfully'

    def __create_model_class(self, field_map, overwrite=False):
        '''
        Function to create a model file in the models dir
        '''
        model_name = format_model_name(self.model)
        # field_map = self.table_map[self.model]['fields']
        fields = field_map.keys()
        
        # define_fields = "\n".join(
        #     f"        self.{field} = None" for field in fields
        # )
        define_fields = "\n".join(
            f"    {field} = {self.__get_field_arguments(field_map[field])}" for field in fields
        )

        
        fk_attr_string = """\n        from models.{fk_model} import {fk_class}
        {field} = kwargs.get('{field}', None)
        self.{fk_model} = {fk_class}.fetch_one({fk_model}_id={fk_model}_id)
        """
        attr_string = "        self.{field} = kwargs.get('{field}', None)"

        # get_from_kwargs = "\n".join(
        #     f"      self.{field} = kwargs.get('{field}', None)" for field in fields
        # )
        get_from_kwargs = "\n".join(
            # for each field, check if fk contraint is {} or fk[pk_only] is true then use attr_string template else get fk[to] and use fk_attr_string template
            attr_string.format(field=field) if field_map.get(field, {}).get('fk', {}) == {} or field_map.get(field).get('fk', {}).get('pk_only') else fk_attr_string.format(field=field, fk_model=field_map.get(field).get('fk', {}).get('to'), fk_class=field_map.get(field).get('fk', {}).get('to').title()) for field in fields
        )
        


        content = f'''import time
import inspect
from typing import Self
from database.db import InitDB
from database import fields
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
{define_fields}

    def __init__(self, using=None, **kwargs):
        super().__init__(**kwargs)
        
        try:
            self._validate()
        except ValidationError as err:
            self._reset_fields()
            logger.exception(str(err.message))
            self.write_error(str(err.message))
            raise err

    def __str__(self):
        return self.model_name

    def _get_from_kwargs(self, **kwargs) -> None:
{get_from_kwargs}


    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)

    def update(self) -> None:
        self._validate(check_id=True)
        super().update()

'''

        file_path = os.path.join('models', f'{self.model}.py')
        
        if os.path.isfile(file_path) and not overwrite:
            # so that we wont overwrite existing model
            return
        
        with open(file_path, mode='w', encoding='utf-8') as file:
            file.write(content)

    def validate_field_map(self, field_map):
        '''Validator for field map'''

        if field_map == {} or 'fields' not in field_map.keys():
            # expect field attr in field map
            raise Exception('Invalid field map. field is required')
        
        if not isinstance(field_map['fields'], dict) or len(list(field_map['fields'].keys())) == 0:
            # field attr dict must not be empty
            raise Exception('Invalid value for field')
        
        for key in field_map['fields'].keys():            
            # get datatype from field
            try:
                datatype = field_map['fields'][key]['datatype']
            except KeyError as err:
                raise Exception('Datatype field is required')
            
            field_name = get_field_from_datatype(datatype)
            if not field_name:
                raise Exception(f'There is no Field for the datatype {datatype}')

            field_contraint = get_contraint_keys_by_field_name(field_name)
        
            # field attr dict must have the required contraint keys
            if not set(field_map['fields'][key].keys()) <= field_contraint:
               raise Exception(f'Invalid contraint {set(field_map['fields'][key].keys()) - field_contraint} provided in {key}\n {field_map['fields'][key]}\n\nRequired Contraints\n {field_contraint}')
            
            # validate foreign key
            # if key == 'fk':
            #     fk_field = field_map['fields'].get(key, {})
            #     required_fk_keys = get_contraint_keys(fk_only=True)
                
            #     if fk_field != {} and not set(fk_field.keys()) <= required_fk_keys:
            #         raise Exception(f'Invalid foreign key attributes {set(fk_field.keys()) - required_fk_keys}')
                
            #     if fk_field.get('to', None) is None:
            #         raise Exception('Forign key {"to"} field is required for relationship')

    def __get_field_arguments(self, fieldmap):
        from database.fields import get_field_from_datatype, get_contraint_keys_by_field_name
        
        field = get_field_from_datatype(fieldmap.pop('datatype', None))

        constraint_keys = get_contraint_keys_by_field_name(field)

        string = f'fields.{field}({', '.join(f'{key} = {value if not isinstance(value, str) else f"'{value}'"}' for key, value in fieldmap.items() if key in constraint_keys)})'
        
        return string

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