import logging

logger = logging.getLogger(__name__)


class ServiceManager:
    def __init__(self, model=None, command=None, validated_args=None, required_args=None, context=None, headers=None, meta=None):
        self.model = model
        self.command = command
        self.validated_args = validated_args
        self.required_args = required_args
        self.context = context
        self.headers = headers
        self.meta = meta

        self.__get_model_object()

    def __get_model_object(self):
        import importlib

        try:
            module = importlib.import_module(f'models.{self.model}')
            model_class = getattr(module, self.model.title())
            if model_class:
                self.model_class = model_class

        except Exception as e:
            logger.error(f'Unable to import module {e}')
            print(e)
            return self.failure(message=str(e), error=e)

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
    
    def get_data_from_instance(self, instances=None):
        if instances is None:
            return instances
        
        if not isinstance(instances, list):
            return instances.data
        
        if len(instances) == 0:
            return instances
        
        data_list = []
        for instance in instances:
            data_list.append(instance.data)
        return data_list

    def process_command(self):
        match self.command.lower():
            case 'create':
                return self.process_create()
            case 'update':
                return self.process_create(update=True)
            case 'delete':
                return self.process_delete()
            case _:    
                return self.process_model_object_function()
    
    def process_create(self, update=False):
        payload = self.validated_args['payload']
        action = 'created'

        try:
            if not update:
                instance = self.model_class(**payload)
                instance.save()
            else:
                action = 'updated'

                object_func = getattr(self.model_class, 'fetch_one')

                kwargs = {
                    f'{self.model_class.model_name}_id': payload[f'{self.model_class.model_name}_id']
                }

                instance = object_func(**kwargs)
                if instance is None:
                    return self.failure(message=f'No record found in {self.model_class.model_name} with ')
                payload.pop(f'{self.model_class.model_name}_id', None)
                for key, value in payload.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                instance.update()
                
            return self.success(message=f'{self.model_class.model_name} {action} successfully')
        except Exception as err:
            print(err)
            return self.failure(message=str(err), error=err)
        
    def process_delete(self):
        payload = self.validated_args['payload']

        try:
            object_func = getattr(self.model_class, 'fetch_one')

            kwargs = {
                f'{self.model_class.model_name}_id': payload[f'{self.model_class.model_name}_id']
            }

            instance = object_func(**kwargs)
            if instance is None:
                return self.failure(message=f'No record found in {self.model_class.model_name} with ')

            instance.delete()
                
            return self.success(message=f'{self.model_class.model_name} deleted successfully')
        except Exception as err:
            print(err)
            return self.failure(message=str(err), error=err)
        
    def process_model_object_function(self):
        payload = self.validated_args['payload']
        object_func = getattr(self.model_class, self.command.lower())
        try:
            if 'payload' in self.required_args:
                instances = object_func(**payload)
            else:
                instances = object_func()
            data = self.get_data_from_instance(instances)

            return self.success(message=f'{self.command} completed on {self.model_class.model_name} successfully', data=data)
        except Exception as err:
            print(err)
            return self.failure(message=str(err), error=err)
        

def main(**data):
    model = data['validated_args']['model']
    service = ServiceManager(model=model, **data)
    return service.process_command()



# python main.py --command CREATE \
# --model client \
# --payload '{"first_name": "Oluwaseyi", "last_name": "Olukosi", "company_name": "Bshp Tech and AI Services", "email": "oluwaseyiolukosi7@gmail.com", "phone": "08104766662", "display_name": "client"}'

# client_id : 27486963-2092-4492-a0b8-64fca4af7a33


# python main.py --command UPDATE \
# --model client \
# --payload '{"client_id": "27486963-2092-4492-a0b8-64fca4af7a33", "first_name": "Oluwaseyi", "last_name": "Olukosi Bshp", "company_name": "Bshp Tech and AI Services", "email": "oluwaseyiolukosi7@gmail.com", "phone": "08104766662", "display_name": "client"}'


# python main.py --command CREATE \
# --model client \
# --payload '{"first_name": "Test", "last_name": "User", "company_name": "Bshp Tech and AI Services", "email": "oluwaseyiolukosi7@gmail.com", "phone": "08104766622", "display_name": "client"}'


# python main.py --command DELETE \
# --model client \
# --payload '{"client_id": "5ec6fd34-82b9-4b4d-b060-07998d852515"}'
