from signal import signal, SIGINT
from sys import exit


def SIGINT_handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

def register_handlers():
    signal(SIGINT, SIGINT_handler)