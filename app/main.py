import logging
from configs.app_config import BASE_DIR
from backend.commands import process_commands
import argparse
import json
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
# - python main.py --command TESTS -> to run backend / test
# - python main.py --command TESTS --model client -> to run test on client table
# - python main.py --command FETCH_ALL client -> to run backend / GET request on client
# - python main.py --command FETCH_ONE --model client --payload {"client_id": 2} -> to run backend / GET request on client ID 2

parser = argparse.ArgumentParser(description="Entry point for cr8tive backend")

parser.add_argument("--model", type=str, help="The model name to query from")
parser.add_argument("--command", type=str, help="The command to run in the model")
parser.add_argument("--payload", type=json.loads, help="Data required to run the command")
parser.add_argument("--header", type=json.loads, help="Context for the current request")
parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
# parser.add_argument("--help", action="store_true", help="Show help")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
parser.add_argument("--count", type=int, default=1, help="Number of times")

args = parser.parse_args()

if args.verbose:
    print("Verbose mode ON")

if args.payload and not isinstance(args.payload, dict):
    raise ValueError('Invalid type for payload argument')

arg_dict = {
    'command': args.command,
    'model': args.model,
    'payload': args.payload,
    'header': args.header,
    'verbose': args.verbose,
    'debug': args.debug
}

if __name__ == '__main__':
    # process_commands(*sys.argv)
    response = process_commands(**arg_dict)
    print(response)