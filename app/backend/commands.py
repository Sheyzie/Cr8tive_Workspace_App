from .arguments import ACTION_MAP, MODULE_MAP
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
    def __init__(self, command):
        super().__init__()
        self.command = command
        self.command_module = self._get_command_module()
        self.start_subprocess()

    

    def _get_command_module(self):
        import importlib

        try:
            module = importlib.import_module(MODULE_MAP.get(self.command))
            # print(module)
            return module
        except Exception as e:
            logger.error(f'Unable to import module {self.command}')
            logger.error(f'Unable to import module {e}')
            self.stderr.write('Unable to import module\n')
            self.stderr.write(f'{e}\n')
            self.stderr.flush()
            exit(1)

    def start_subprocess(self):
        import subprocess
        self.command_module.main()
        exit(0)

class Commands(BaseProcess):
    def __init__(self, args: list):
        super().__init__()
        self.args: list = args
        self._validate_args()
        self._run_command_from_action()

    def _validate_args(self):
        if len(self.args) < 2:
            logger.error('Invalid argument length supplied')
            raise Exception(f'''
            Invalid length of arguments supplied.
            Enter -- python main.py help -- for help
        ''')

        if len(self.args) == 2 and self.args[1] == 'help':
            self.stdout.write('All help comes from the Lord ✌🏾' + '\n')
            exit(1)

        elif len(self.args) == 2 and self.args[1] != 'help':
            self.stdout.write('You are to old for this for crying out loud' + '\n')
            exit(1)

        self.entry_point: str = self.args[0]
        self.action: str = self.args[1]
        self.command: str = self.args[2]

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
        self.stdout.write(self.command + '\n')
        self.stdout.flush()
        processor = Processor(self.command)

        



def process_commands(args: list):
    logger.info('Running backend command...')
    command = Commands(args)