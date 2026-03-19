import logging
from configs.app_config import BASE_DIR
from backend.commands import process_commands
import sys


# logger setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "logs/app.log"),
        # logging.StreamHandler() # to log to console
    ]
)

# python main.py command [arguments] -> syntax
# - python main.py test -> to run backend / test
# - python main.py test client -> to run test on client table
# - python main.py GET client -> to run backend / GET request on client
# - python main.py GET client 2 -> to run backend / GET request on client ID 2

if __name__ == '__main__':
    process_commands(*sys.argv)

    arg_dict = {
        'arguments': ['test'],
        'entry_point': 'main.py',
        'base_command': 'test'
    }
    # process_commands(**arg_dict)