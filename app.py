import platform
import sys
import threading
import time
import csv
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, send_file
from flask_socketio import SocketIO, emit
from queue import Queue

def get_plux_binary_path():
    """Determine the correct PLUX API binary path based on OS, architecture, and Python version."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Detect architecture
        machine = platform.machine()
        if machine == "arm64":
            # Apple Silicon (M1, M2, etc.)
            arch_prefix = "M1"
        else:
            # Intel
            arch_prefix = "Intel"
        
        # Get Python version (major.minor, e.g., "311" for 3.11)
        py_version = ''.join(platform.python_version_tuple()[:2])
        
        return f"{arch_prefix}_{py_version}"
    
    elif system == "Linux":
        machine = platform.machine()
        if machine == "x86_64":
            return "Linux64"
        elif machine == "aarch64":
            # Check Python version for ARM32/ARM64
            py_version = ''.join(platform.python_version_tuple()[:2])
            if py_version == "38":
                return "LinuxARM64_38"
            elif py_version == "39":
                return "LinuxARM64_39"
            else:
                return "LinuxARM64_38"  # fallback
        elif "arm" in machine:
            py_version = ''.join(platform.python_version_tuple()[:2])
            if py_version == "311":
                return "LinuxARM32_311"
            else:
                return "LinuxARM32"
    
    elif system == "Windows":
        arch = platform.architecture()[0][:2]  # "32" or "64"
        py_version = ''.join(platform.python_version_tuple()[:2])
        return f"Win{arch}_{py_version}"
    
    raise OSError(f"Unsupported platform: {system}")

# Configure path for PLUX API
binary_path = get_plux_binary_path()
print(f"Using PLUX API binary path: {binary_path}")
sys.path.append(f"PLUX-API-Python3/{binary_path}")

import plux

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bitalino-mvp-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Create recordings directory
RECORDINGS_DIR = 'recordings'
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)

# Global variables
data_queue = Queue(maxsize=1000)
acquisition_active = False
current_recording_data = []
current_recording_metadata = {}
device_status = {
    'connected': False,
    'battery': 0,
    'frequency': 0,
    'channel': 0,
    'samples_received': 0,
    'error': None
}


class BITalinoDevice(plux.SignalsDev):
    def __init__(self, address):
        plux.MemoryDev.__init__(address)
        self.frequency = 0
        self.running = False

    def onRawFrame(self, nSeq, data):
        """Called for each frame of data received from BITalino"""
        if self.running:
            # Extract ECG value (first channel)
            ecg_value = data[0] if len(data) > 0 else 0
            current_time = time.time()

            # Store data for CSV recording
            current_recording_data.append({
                'sequence': nSeq,
                'value': ecg_value,
                'timestamp': current_time
            })

            # Put data in queue for web clients
            if not data_queue.full():
                data_queue.put({
                    'sequence': nSeq,
                    'value': ecg_value,
                    'timestamp': current_time
                })

            # Update sample count
            device_status['samples_received'] = nSeq

        return not self.running

    def stop_acquisition(self):
        """Stop the acquisition loop"""
        self.running = False


# Global device instance
bitalino_device = None
acquisition_thread = None


def acquisition_worker(address, frequency, channel_code):
    """Worker function to run BITalino acquisition in background"""
    global bitalino_device, acquisition_active, device_status, current_recording_data, current_recording_metadata

    try:
        # Create device instance
        bitalino_device = BITalinoDevice(address)
        bitalino_device.frequency = frequency
        bitalino_device.running = True

        # Get battery level
        battery = bitalino_device.getBattery()
        device_status['battery'] = int(battery)
        device_status['connected'] = True
        device_status['frequency'] = frequency
        device_status['channel'] = channel_code
        device_status['error'] = None

        # Store metadata for this recording
        start_time = datetime.now()
        current_recording_metadata = {
            'start_time': start_time,
            'frequency': frequency,
            'channel_code': channel_code,
            'battery': battery,
            'address': address
        }

        print(f"Battery level: {battery}%")
        print(f"Starting acquisition at {frequency}Hz on channel code {hex(channel_code)}")

        # Start acquisition
        bitalino_device.start(frequency, channel_code, 16)

        # Emit status update
        socketio.emit('status_update', device_status)

        # Run acquisition loop
        bitalino_device.loop()

        # Stop and cleanup
        bitalino_device.stop()
        bitalino_device.close()

        device_status['connected'] = False
        acquisition_active = False

        # Save recording to CSV
        save_recording_to_csv(start_time)

        print("Acquisition stopped and saved")

    except Exception as e:
        print(f"Acquisition error: {e}")
        device_status['error'] = str(e)
        device_status['connected'] = False
        acquisition_active = False
        socketio.emit('status_update', device_status)


def save_recording_to_csv(start_time):
    """Save recorded data to CSV file"""
    global current_recording_data, current_recording_metadata

    if not current_recording_data:
        print("No data to save")
        return None

    # Generate filename with timestamp
    filename = f"ecg_recording_{start_time.strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(RECORDINGS_DIR, filename)

    try:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write metadata header
            writer.writerow(['# BITalino ECG Recording'])
            writer.writerow(['# Start Time', start_time.strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['# Frequency (Hz)', current_recording_metadata.get('frequency', 'N/A')])
            writer.writerow(['# Channel Code', hex(current_recording_metadata.get('channel_code', 0))])
            writer.writerow(['# Battery (%)', current_recording_metadata.get('battery', 'N/A')])
            writer.writerow(['# Device Address', current_recording_metadata.get('address', 'N/A')])
            writer.writerow(['# Total Samples', len(current_recording_data)])
            writer.writerow([])  # Empty line

            # Write data header
            writer.writerow(['Sequence', 'ECG Value', 'Timestamp'])

            # Write data rows
            for sample in current_recording_data:
                writer.writerow([
                    sample['sequence'],
                    sample['value'],
                    sample['timestamp']
                ])

        print(f"Recording saved: {filepath}")

        # Emit update to clients about new recording
        socketio.emit('new_recording', {
            'filename': filename,
            'samples': len(current_recording_data),
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

        return filename

    except Exception as e:
        print(f"Error saving recording: {e}")
        return None


@app.route('/')

def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current device status"""
    return jsonify(device_status)


@app.route('/api/recordings')
def list_recordings():
    """List all available recordings"""
    recordings = []

    if os.path.exists(RECORDINGS_DIR):
        for filename in os.listdir(RECORDINGS_DIR):
            if filename.endswith('.csv'):
                filepath = os.path.join(RECORDINGS_DIR, filename)
                file_stats = os.stat(filepath)

                # Read first few lines to get metadata
                metadata = {}
                try:
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                        for line in lines[:10]:  # Read first 10 lines for metadata
                            if line.startswith('# Start Time'):
                                metadata['start_time'] = line.split(',', 1)[1].strip()
                            elif line.startswith('# Frequency'):
                                metadata['frequency'] = line.split(',', 1)[1].strip()
                            elif line.startswith('# Total Samples'):
                                metadata['samples'] = line.split(',', 1)[1].strip()
                except:
                    pass

                recordings.append({
                    'filename': filename,
                    'size': file_stats.st_size,
                    'created': file_stats.st_ctime,
                    'metadata': metadata
                })

    # Sort by creation time, newest first
    recordings.sort(key=lambda x: x['created'], reverse=True)

    return jsonify(recordings)


@app.route('/api/recordings/<filename>')
def download_recording(filename):
    """Download a specific recording"""
    # Security: prevent directory traversal
    filename = os.path.basename(filename)
    filepath = os.path.join(RECORDINGS_DIR, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'Recording not found'}), 404

    return send_file(filepath, as_attachment=True, download_name=filename)


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status_update', device_status)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('start_acquisition')
def handle_start_acquisition(data):
    """Start BITalino acquisition"""
    global acquisition_active, acquisition_thread, device_status, current_recording_data

    if acquisition_active:
        emit('error', {'message': 'Acquisition already running'})
        return

    # Get parameters from client
    address = data.get('address', '98:D3:C1:FD:ED:B7')
    frequency = data.get('frequency', 1000)
    channel_code = data.get('channel_code', 0x01)

    # Reset status
    device_status['samples_received'] = 0
    device_status['error'] = None

    # Clear data queue and recording data
    while not data_queue.empty():
        data_queue.get()
    current_recording_data = []

    # Start acquisition in background thread
    acquisition_active = True
    acquisition_thread = threading.Thread(
        target=acquisition_worker,
        args=(address, frequency, channel_code),
        daemon=True
    )
    acquisition_thread.start()

    emit('status_update', device_status)


@socketio.on('stop_acquisition')
def handle_stop_acquisition():
    """Stop BITalino acquisition"""
    global bitalino_device, acquisition_active

    if bitalino_device and acquisition_active:
        bitalino_device.stop_acquisition()
        acquisition_active = False
        emit('status_update', device_status)


def data_broadcast_worker():
    """Background worker to broadcast data to all connected clients"""
    while True:
        if not data_queue.empty():
            # Get data from queue
            data = data_queue.get()

            # Broadcast to all connected clients
            socketio.emit('new_data', data)
        else:
            # Small sleep to prevent busy waiting
            time.sleep(0.001)


# Start data broadcast worker
broadcast_thread = threading.Thread(target=data_broadcast_worker, daemon=True)
broadcast_thread.start()


if __name__ == '__main__':
    print("Starting BITalino MVP Server...")
    print("Open http://localhost:5001 in your browser")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=False)
