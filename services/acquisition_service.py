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

    def start(self, address, frequency, channels):
        """
        Start data acquisition from BITalino device.

        Args:
            address: Device Bluetooth address
            frequency: Sampling frequency in Hz
            channels: List of channel config dicts with keys: port, enabled, type, label
        """
        if self.is_active:
            raise RuntimeError("Acquisition already running")

        active_ports = [c['port'] for c in channels if c.get('enabled', False)]
        if not active_ports:
            raise ValueError("No channels enabled. Please enable at least one channel.")

        channel_labels = {c['port']: c.get('label', f"A{c['port']}") for c in channels}
        channel_types = {c['port']: c.get('type', 'RAW') for c in channels}

        # Reset status and data
        self.status.reset()
        self.recording_data = []

        # Clear data queue
        while not self.data_queue.empty():
            self.data_queue.get()

        self.is_active = True
        self.acquisition_thread = threading.Thread(
            target=self._acquisition_worker,
            args=(address, frequency, active_ports, channel_labels, channel_types),
            daemon=True
        )
        self.acquisition_thread.start()

    def stop(self):
        """Stop data acquisition."""
        if self.device and self.is_active:
            self.device.stop_acquisition()
            self.is_active = False

    def _acquisition_worker(self, address, frequency, active_ports, channel_labels, channel_types):
        """
        Worker function to run BITalino acquisition in background.

        Args:
            address: Device Bluetooth address
            frequency: Sampling frequency in Hz
            active_ports: Ordered list of port numbers to activate
            channel_labels: Dict mapping port number to display label
            channel_types: Dict mapping port number to signal type string
        """
        try:
            # Create device instance
            self.device = BITalinoDevice(address)
            self.device.data_queue = self.data_queue
            self.device.recording_data = self.recording_data
            self.device.frequency = frequency
            self.device.active_ports = active_ports
            self.device.running = True

            # Get battery level
            battery = self.device.getBattery()
            self.status.battery = int(battery)
            self.status.connected = True
            self.status.frequency = frequency
            self.status.active_ports = active_ports
            self.status.error = None

            # Store metadata for this recording
            start_time = datetime.now()
            self.recording_metadata = {
                'start_time': start_time,
                'frequency': frequency,
                'active_ports': active_ports,
                'channel_labels': channel_labels,
                'channel_types': channel_types,
                'battery': battery,
                'address': address
            }

            print(f"Battery level: {battery}%")
            print(f"Starting acquisition at {frequency}Hz on ports {active_ports}")

            # Trigger the start of the data recording:
            # https://www.downloads.plux.info/apis/PLUX-API-Python-Docs/classplux_1_1_signals_dev.html#a028eaf160a20a53b3302d1abd95ae9f1
            # Note: nBits (16) is ignored for BITalino devices.
            self.device.start(frequency, active_ports, 16)

            # Emit status update
            self.socketio.emit('status_update', self.get_status())

            # Run acquisition loop (calls device.onRawFrame until it returns True)
            self.device.loop()

            # Stop and cleanup
            self.device.stop()
            self.device.close()

            self.status.connected = False
            self.is_active = False
            self.socketio.emit('status_update', self.get_status())

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
            self.socketio.emit('status_update', self.get_status())

    def get_status(self):
        """
        Get current device status.

        Returns:
            dict: Current status dictionary
        """
        if self.device and self.is_active:
            self.status.samples_received = len(self.recording_data)

        return self.status.to_dict()
