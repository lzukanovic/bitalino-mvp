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
        self.active_ports = []
        self.samples_received = 0
        self.error = None

    def to_dict(self):
        """Convert status to dictionary for JSON serialization."""
        return {
            'connected': self.connected,
            'battery': self.battery,
            'frequency': self.frequency,
            'active_ports': self.active_ports,
            'samples_received': self.samples_received,
            'error': self.error
        }

    def reset(self):
        """Reset status to default values."""
        self.connected = False
        self.battery = 0
        self.frequency = 0
        self.active_ports = []
        self.samples_received = 0
        self.error = None


class BITalinoDevice(plux.BITalinoDev):
    """
    BITalino device class for managing device communication and data acquisition.
    """

    def __init__(self, address):
        """
        Initialize BITalino device.

        Args:
            address: Device Bluetooth address
        """
        plux.BITalinoDev.__init__(address)
        self.frequency = 0
        self.running = False
        self.data_queue = None
        self.recording_data = None
        self.active_ports = []  # Ordered list of active port numbers

    def onRawFrame(self, nSeq, data):
        """
        Called for each frame of data received from BITalino.

        Args:
            nSeq: Sequence number of the frame
            data: List of channel values ordered by active_ports

        Returns:
            bool: True to stop acquisition, False to continue
        """
        if self.running:
            current_time = time.time()

            # Map data values to their port numbers
            channel_values = {}
            for i, port in enumerate(self.active_ports):
                channel_values[port] = data[i] if i < len(data) else 0

            # Store data for CSV recording
            self.recording_data.append({
                'sequence': nSeq,
                'channels': channel_values,
                'timestamp': current_time
            })

            # Put data in queue for web clients (non-blocking)
            if not self.data_queue.full():
                self.data_queue.put({
                    'sequence': nSeq,
                    'channels': channel_values,
                    'timestamp': current_time
                })

        return not self.running

    def stop_acquisition(self):
        """Stop the acquisition loop."""
        self.running = False
