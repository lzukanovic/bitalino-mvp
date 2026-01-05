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
DEFAULT_FREQUENCY = 1000  # Hz
DEFAULT_CHANNEL_CODE = 0x01  # Channel 1 (ECG)

# Data queue configuration
DATA_QUEUE_MAX_SIZE = 1000

# Recording configuration
RECORDINGS_DIR = 'recordings'

# Ensure recordings directory exists
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
