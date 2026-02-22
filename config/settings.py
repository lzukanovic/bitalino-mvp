"""
Application configuration settings.
"""
import os

# Flask configuration
SECRET_KEY = 'bitalino-mvp-secret'
HOST = '0.0.0.0'
PORT = 5001
DEBUG = True

# SocketIO configuration
SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
SOCKETIO_ASYNC_MODE = 'threading'

# BITalino device configuration
DEFAULT_DEVICE_ADDRESS = '98:D3:C1:FD:ED:B7'
DEFAULT_FREQUENCY = 100  # Hz
# Default channel configuration for 6 analog ports.
# BITalino hardware resolution: Ports 1-4 are 10-bit, Ports 5-6 are 6-bit.
DEFAULT_CHANNELS = [
    {'port': 1, 'enabled': True,  'type': 'RAW', 'label': 'A1'},
    {'port': 2, 'enabled': False, 'type': 'RAW', 'label': 'A2'},
    {'port': 3, 'enabled': False, 'type': 'RAW', 'label': 'A3'},
    {'port': 4, 'enabled': False, 'type': 'RAW', 'label': 'A4'},
    {'port': 5, 'enabled': False, 'type': 'RAW', 'label': 'A5'},
    {'port': 6, 'enabled': False, 'type': 'RAW', 'label': 'A6'},
]

# Data queue configuration
DATA_QUEUE_MAX_SIZE = 1000

# Recording configuration
RECORDINGS_DIR = 'recordings'

# Ensure recordings directory exists
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
