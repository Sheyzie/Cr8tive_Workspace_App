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
    def __init__(self, base_command={}, arguments=[]):
        super().__init__()
        self.data = {}
        self.base_command = base_command
        self.arguments = deque(arguments)
        self.base_command_module = self._get_command_module()
        self._set_data()
        self.start_subprocess()

    def _get_command_module(self):
        import importlib

        try:
            module = importlib.import_module(self.base_command.get('module'))

            return module
        except Exception as e:
            logger.error(f'Unable to import module {self.command}')
            logger.error(f'Unable to import module {e}')
            self.stderr.write('Unable to import module\n')
            self.stderr.write(f'{e}\n')
            self.stderr.flush()
            exit(1)

    def _set_data(self):
        self.data = {
            'command': self.base_command.get('name', None),
            'module': self.base_command.get('module', None),
            'validated_args': self.base_command.get('validated_args', {}),
        }

    def start_subprocess(self):
        import subprocess

        self.base_command_module.main(**self.data)
        exit(0)

class Commands(BaseProcess):
    arguments: list = None
    entry_point: str = None
    command: str = None
    base_command: dict = None

    def __init__(self, entry_point=None, command=None, *args, **kwargs):
        super().__init__()
        self.arguments = []
        self.entry_point = entry_point
        self.command = command

        if args or kwargs:
            self._process_args(*args, **kwargs)

        self._validate_args()
        self._run_command()

    def _process_args(self, *args, **kwargs):
        arguments = deque(args)
        if self.entry_point is None:
            self.entry_point = arguments.popleft()
        if self.command is None:
            self.command = arguments.popleft()
        if len(self.arguments) == 0:
            self.arguments = list(arguments)

        entry_point = kwargs.get('entry_point', None)
        if self.entry_point is None:
            self.entry_point = entry_point
        command = kwargs.get('command', None)
        if self.command is None:
            self.command = command

        arguments = deque(kwargs.get('arguments', []))
        if len(self.arguments) == 0:
            self.arguments = list(arguments)

    def _validate_args(self):
        self.stdout.write('\rValidating commands...')
        # get base command
        base_command = BASE_COMMANDS.get(self.command, None)

        # check if base command exist
        if not base_command:
            raise Exception(f'Invalid command {self.command}')

        # validate base command arguments
        if base_command.get('has_args'):
            # check length of provided argument
            expected_args = base_command.get('args')
  
            if len(expected_args.keys()) < len(self.arguments):
                raise Exception(f'Too many arguments provided for command {self.command}')
            
            # validate required arguement
            required_args = base_command.get('require_args')
            if len(required_args) > len(self.arguments):
                raise Exception(f'Not enough arguments provided for command {self.command}')
            
            validated_args = {}
            for arg in expected_args:
                validator = expected_args.get(arg).get('validate')
                if validator and not validator(self.arguments):
                    raise Exception(f'Invalid argument for field {arg}')
                
                validated_args[arg] = self.arguments

        # add validated argument to base command
        base_command['validated_args'] = validated_args
        self.base_command = base_command
        self.stdout.write('\rValidation completed\n')
        self.stdout.flush()

    def _run_command_from_action(self):
        
        try:
            if ACTION_MAP.get(self.action) == self.command:
                self._run_command()
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

    def _run_command(self):
        self.stdout.write(f'\nRunning {self.base_command.get('name')} command...\n')
        self.stdout.flush()
        if not self.base_command:
            raise Exception(f'No base command provided for {self.command}\n')
        
        processor = Processor(self.base_command, self.arguments)


def process_commands(*args, **kwargs):
    logger.info('Running backend command...')
    command = Commands(*args, **kwargs)