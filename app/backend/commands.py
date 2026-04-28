from collections import deque
from .arguments import ACTION_MAP, MODULE_MAP, BASE_COMMANDS
from configs.app_config import BASE_DIR
import sys
import time
import logging

logger = logging.getLogger(__name__)

# for i in range(5):
#     sys.stdout.write(f"\rProgress: {i * '#'}")
#     sys.stdout.flush()
#     time.sleep(1)

class BaseProcess:
    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr


class Processor(BaseProcess):
    def __init__(self, base_command={}):
        super().__init__()
        self.data = {}
        self.base_command = base_command
        self.module = self._get_command_module()
        self._set_data()

    def _get_command_module(self):
        import importlib

        try:
            command = BASE_COMMANDS.get(self.base_command.get('command'))
            module = importlib.import_module(command['module'])
            return module
        except Exception as e:
            logger.error(f'Unable to import module {command} command')
            logger.error(f'Unable to import module {e}')
            self.stderr.write('Unable to import module\n')
            self.stderr.write(f'{e}\n')
            self.stderr.flush()
            exit(1)

    def _set_data(self):
        self.data = {
            **self.base_command,
            'meta': {
                'module': self.module
            }
        }

    def start_subprocess(self):
        return self.module.main(**self.data)


class Commands(BaseProcess):
    command: str = None
    model: str = None
    payload: str = None
    header: str = None
    verbose: bool = False
    debug: bool = False
    base_command: dict = None

    def __init__(self, *args, **kwargs):
        super().__init__()

        if args or kwargs:
            self._process_args(*args, **kwargs)

        self._validate_args()
        

    def _process_args(self, *args, **kwargs):
        if len(args) > 0:
            arguments = deque(args)
            if self.command is None:
                self.command = arguments.popleft()
            if self.model is None:
                self.model = arguments.popleft()
            if self.payload is None:
                self.payload = arguments.popleft()
            if self.header is None:
                self.header = arguments.popleft()
            if self. verbose is None:
                self.verbose = arguments.popleft()
            if self.debug is None:
                self.debug = arguments.popleft()
        
        if kwargs:
            command = kwargs.get('command', None)
            if self.command is None:
                self.command = command
            model = kwargs.get('model', None)
            if self.model is None:
                self.model = model
            payload = kwargs.get('payload', None)
            if self.payload is None:
                self.payload = payload
            header = kwargs.get('header', None)
            if self.header is None:
                self.header = header
            verbose = kwargs.get('verbose', None)
            if self. verbose is None:
                self.verbose = verbose
            debug = kwargs.get('debug', None)
            if self.debug is None:
                self.debug = debug

    def _validate_args(self):
        self.stdout.write('Validating commands...')
        # get base command
        base_command = BASE_COMMANDS.get(self.command, None)

        # check if base command exist
        if not base_command:
            raise Exception(f'Invalid command {self.command}')

        # validate base command arguments
        if base_command.get('has_args'):
            # check length of provided argument
            expected_args = base_command.get('args')

            for key in expected_args.keys():
                if not hasattr(self, key):
                    raise Exception(f'{key} argument is not valid')
                # raise Exception(f'Too many arguments provided for command {self.command}')

            # validate required arguement
            required_args = base_command.get('require_args')
            
            for arg in required_args:
                value = getattr(self, arg)
                if not value:
                    raise Exception(f'{value} received for a required argument {arg}')
                
                validator = expected_args.get(arg).get('validate', None)
                
                if validator:
                    if arg == 'payload':
                        is_valid = validator(set(value.keys()), self.model)
                    else:
                        is_valid = validator(getattr(self, arg))
                    if not is_valid:
                        raise Exception(f'Invalid argument for field {arg}')
                

        # add validated argument to base command
        base_command = {
            'command': self.command,
            'validated_args': {
                'model': self.model,
                'payload': self.payload
            },
            'required_args': required_args,
            'context': {
                'verbose': self.verbose,
                'debug': self.debug
            },
            'headers': self.header
        }
        self.base_command = base_command
        self.stdout.write('\rValidation completed\n')
        self.stdout.flush()

    def _run_command_from_action(self):
        
        try:
            if ACTION_MAP.get(self.action) == self.command:
                self.run_command()
            else:
                logger.error('Invalid command argument')
                self.stderr.write('Invalid command arguement\n')
                self.stderr.flush()
                exit(1)
        except Exception as e:
            logger.exception('Error running command')
            self.stdout.write('Error running command\n')
            self.stdout.write(str(e) + '\n')
            self.stdout.flush()
            exit(1)

    def run_command(self):
        self.stdout.write(f'\nRunning {self.base_command.get('command')} command...\n')
        self.stdout.flush()
        if not self.base_command:
            raise Exception(f'No base command provided for {self.command}\n')
        
        processor = Processor(self.base_command)
        return processor.start_subprocess()


def process_commands(*args, **kwargs):
    logger.info('Running backend command...')
    command = Commands(*args, **kwargs)
    return command.run_command()