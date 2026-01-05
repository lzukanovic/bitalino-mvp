"""
BITalino device model and data structures.
"""
import time
from utils.plux_loader import load_plux_library

# Load PLUX library
plux = load_plux_library()


class DeviceStatus:
    """Class to manage device status information."""
    
    def __init__(self):
        self.connected = False
        self.battery = 0
        self.frequency = 0
        self.channel = 0
        self.samples_received = 0
        self.error = None
    
    def to_dict(self):
        """Convert status to dictionary for JSON serialization."""
        return {
            'connected': self.connected,
            'battery': self.battery,
            'frequency': self.frequency,
            'channel': self.channel,
            'samples_received': self.samples_received,
            'error': self.error
        }
    
    def reset(self):
        """Reset status to default values."""
        self.connected = False
        self.battery = 0
        self.frequency = 0
        self.channel = 0
        self.samples_received = 0
        self.error = None


class BITalinoDevice(plux.SignalsDev):
    """
    BITalino device class for managing device communication and data acquisition.
    """
    
    def __init__(self, address, data_queue, recording_data):
        """
        Initialize BITalino device.
        
        Args:
            address: Device Bluetooth address
            data_queue: Queue for real-time data streaming
            recording_data: List to store all recorded data
        """
        plux.MemoryDev.__init__(address)
        self.frequency = 0
        self.running = False
        self.data_queue = data_queue
        self.recording_data = recording_data

    def onRawFrame(self, nSeq, data):
        """
        Called for each frame of data received from BITalino.
        
        Args:
            nSeq: Sequence number of the frame
            data: List of channel values
        
        Returns:
            bool: True to stop acquisition, False to continue
        """
        if self.running:
            # Extract ECG value (first channel)
            ecg_value = data[0] if len(data) > 0 else 0
            current_time = time.time()

            # Store data for CSV recording
            self.recording_data.append({
                'sequence': nSeq,
                'value': ecg_value,
                'timestamp': current_time
            })

            # Put data in queue for web clients (non-blocking)
            if not self.data_queue.full():
                self.data_queue.put({
                    'sequence': nSeq,
                    'value': ecg_value,
                    'timestamp': current_time
                })

        return not self.running

    def stop_acquisition(self):
        """Stop the acquisition loop."""
        self.running = False
