"""
WebSocket event handlers for real-time communication.
"""
from flask_socketio import emit
from config.settings import DEFAULT_DEVICE_ADDRESS, DEFAULT_FREQUENCY, DEFAULT_CHANNELS

# Will be set by main app
acquisition_service = None


def init_socketio_handlers(socketio, acq_service):
    """
    Initialize SocketIO event handlers.
    
    Args:
        socketio: SocketIO instance
        acq_service: AcquisitionService instance
    """
    global acquisition_service
    acquisition_service = acq_service

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        print('Client connected')
        emit('status_update', acquisition_service.get_status())

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        print('Client disconnected')

    @socketio.on('start_acquisition')
    def handle_start_acquisition(data):
        """
        Start BITalino acquisition.
        
        Args:
            data: Dictionary containing acquisition parameters
        """
        try:
            # Get parameters from client with defaults
            address = data.get('address', DEFAULT_DEVICE_ADDRESS)
            frequency = data.get('frequency', DEFAULT_FREQUENCY)
            channels = data.get('channels', DEFAULT_CHANNELS)

            # Start acquisition. The worker thread emits its own status_update
            # once the device is connected, so we don't emit here.
            acquisition_service.start(address, frequency, channels)

        except (RuntimeError, ValueError) as e:
            emit('error', {'message': str(e)})
        except Exception as e:
            print(f"Error starting acquisition: {e}")
            emit('error', {'message': f'Failed to start acquisition: {str(e)}'})

    @socketio.on('stop_acquisition')
    def handle_stop_acquisition():
        """Stop BITalino acquisition."""
        try:
            emit('status_update', acquisition_service.get_status())
            acquisition_service.stop()
        except Exception as e:
            print(f"Error stopping acquisition: {e}")
            emit('error', {'message': f'Failed to stop acquisition: {str(e)}'})
