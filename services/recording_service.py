"""
Service for managing recording files.
"""
import csv
import os
from datetime import datetime
from config.settings import RECORDINGS_DIR


def save_recording_to_csv(recording_data, recording_metadata, start_time, socketio=None):
    """
    Save recorded data to CSV file.
    
    Args:
        recording_data: List of recorded samples
        recording_metadata: Metadata dictionary for the recording
        start_time: Recording start datetime
        socketio: Optional SocketIO instance for emitting events
    
    Returns:
        str: Filename of saved recording, or None if failed
    """
    if not recording_data:
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
            writer.writerow(['# Frequency (Hz)', recording_metadata.get('frequency', 'N/A')])
            writer.writerow(['# Channel Code', hex(recording_metadata.get('channel_code', 0))])
            writer.writerow(['# Battery (%)', recording_metadata.get('battery', 'N/A')])
            writer.writerow(['# Device Address', recording_metadata.get('address', 'N/A')])
            writer.writerow(['# Total Samples', len(recording_data)])
            writer.writerow([])  # Empty line

            # Write data header
            writer.writerow(['Sequence', 'ECG Value', 'Timestamp'])

            # Write data rows
            for sample in recording_data:
                writer.writerow([
                    sample['sequence'],
                    sample['value'],
                    sample['timestamp']
                ])

        print(f"Recording saved: {filepath}")

        # Emit update to clients about new recording
        if socketio:
            socketio.emit('new_recording', {
                'filename': filename,
                'samples': len(recording_data),
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S')
            })

        return filename

    except Exception as e:
        print(f"Error saving recording: {e}")
        return None


def list_recordings():
    """
    List all available recordings with metadata.
    
    Returns:
        list: List of recording dictionaries with metadata
    """
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
                except Exception as e:
                    print(f"Error reading metadata from {filename}: {e}")

                recordings.append({
                    'filename': filename,
                    'size': file_stats.st_size,
                    'created': file_stats.st_ctime,
                    'metadata': metadata
                })

    # Sort by creation time, newest first
    recordings.sort(key=lambda x: x['created'], reverse=True)

    return recordings


def get_recording_path(filename):
    """
    Get the full path for a recording file.
    
    Args:
        filename: Name of the recording file
    
    Returns:
        str: Full path to the recording file, or None if not found
    """
    # Security: prevent directory traversal
    filename = os.path.basename(filename)
    filepath = os.path.join(RECORDINGS_DIR, filename)

    if os.path.exists(filepath):
        return filepath
    return None
