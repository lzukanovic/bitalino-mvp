"""
Service for managing BITalino data acquisition.
"""
import threading
from datetime import datetime
from models.device import BITalinoDevice, DeviceStatus
from services.recording_service import save_recording_to_csv


class AcquisitionService:
    """Service to manage BITalino device acquisition."""
    
    def __init__(self, data_queue, socketio):
        """
        Initialize acquisition service.
        
        Args:
            data_queue: Queue for real-time data streaming
            socketio: SocketIO instance for emitting events
        """
        self.data_queue = data_queue
        self.socketio = socketio
        self.device = None
        self.acquisition_thread = None
        self.is_active = False
        self.status = DeviceStatus()
        self.recording_data = []
        self.recording_metadata = {}
    
    def start(self, address, frequency, channel_code):
        """
        Start data acquisition from BITalino device.
        
        Args:
            address: Device Bluetooth address
            frequency: Sampling frequency in Hz
            channel_code: Channel configuration code
        """
        if self.is_active:
            raise RuntimeError("Acquisition already running")
        
        # Reset status and data
        self.status.reset()
        self.status.samples_received = 0
        self.recording_data = []
        
        # Clear data queue
        while not self.data_queue.empty():
            self.data_queue.get()
        
        # Start acquisition in background thread
        self.is_active = True
        self.acquisition_thread = threading.Thread(
            target=self._acquisition_worker,
            args=(address, frequency, channel_code),
            daemon=True
        )
        self.acquisition_thread.start()
    
    def stop(self):
        """Stop data acquisition."""
        if self.device and self.is_active:
            self.device.stop_acquisition()
            self.is_active = False
    
    def _acquisition_worker(self, address, frequency, channel_code):
        """
        Worker function to run BITalino acquisition in background.
        
        Args:
            address: Device Bluetooth address
            frequency: Sampling frequency in Hz
            channel_code: Channel configuration code
        """
        try:
            # Create device instance
            self.device = BITalinoDevice(address, self.data_queue, self.recording_data)
            self.device.frequency = frequency
            self.device.running = True

            # Get battery level
            battery = self.device.getBattery()
            self.status.battery = int(battery)
            self.status.connected = True
            self.status.frequency = frequency
            self.status.channel = channel_code
            self.status.error = None

            # Store metadata for this recording
            start_time = datetime.now()
            self.recording_metadata = {
                'start_time': start_time,
                'frequency': frequency,
                'channel_code': channel_code,
                'battery': battery,
                'address': address
            }

            print(f"Battery level: {battery}%")
            print(f"Starting acquisition at {frequency}Hz on channel code {hex(channel_code)}")

            # Start acquisition
            self.device.start(frequency, channel_code, 16)

            # Emit status update
            self.socketio.emit('status_update', self.status.to_dict())

            # Run acquisition loop
            self.device.loop()

            # Stop and cleanup
            self.device.stop()
            self.device.close()

            self.status.connected = False
            self.is_active = False

            # Save recording to CSV
            filename = save_recording_to_csv(
                self.recording_data,
                self.recording_metadata,
                start_time,
                self.socketio
            )

            print(f"Acquisition stopped and saved as {filename}")

        except Exception as e:
            print(f"Acquisition error: {e}")
            self.status.error = str(e)
            self.status.connected = False
            self.is_active = False
            self.socketio.emit('status_update', self.status.to_dict())
    
    def get_status(self):
        """
        Get current device status.
        
        Returns:
            dict: Current status dictionary
        """
        # Update samples count if device is active
        if self.device and self.is_active:
            self.status.samples_received = len(self.recording_data)
        
        return self.status.to_dict()
