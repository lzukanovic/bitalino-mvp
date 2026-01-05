# BITalino ECG Monitor - MVP

A web-based platform for real-time physiological signal acquisition and visualization using the PLUX BITalino system.

## Features

- **Real-time ECG Visualization**: Live chart displaying ECG signals from BITalino analog input channel 1
- **Device Status Monitoring**:
  - Connection status with visual indicators
  - Battery level monitoring
  - Sample rate display
  - Total samples received counter
- **Data Recording & Export**:
  - Automatic CSV recording of all acquisitions
  - Recordings include metadata (timestamp, frequency, battery, sample count)
  - Download recordings directly from web interface
  - Organized recordings list with file info
- **Web-based Interface**: Access from any browser on your local network
- **WebSocket Communication**: Low-latency real-time data streaming
- **Configurable Acquisition**:
  - Custom device MAC address
  - Adjustable sample frequency

## Prerequisites

- Python (tested on Mac M1 with 3.11)
- PLUX BITalino device
- ECG sensor connected to analog input A1

## Installation

1. Navigate to the project directory:

```bash
cd bitalino-mvp
```

2. Install required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration

Before running, ensure your BITalino device is:

1. Powered on
2. Bluetooth is enabled on your computer
3. Device is paired (MAC address default: `98:D3:C1:FD:ED:B7`)

You can find your device's MAC address:

- **macOS**: System Preferences > Bluetooth
- **Linux**: `bluetoothctl devices`
- **Windows**: Device Manager > Bluetooth

Or inside of PLUX BioSignals app when connected.

## Usage

1. Start the Flask server:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5001
```

3. Configure acquisition parameters:

   - **Device MAC Address**: Enter your BITalino's MAC address
   - **Frequency**: Set sampling rate (1000 Hz recommended for ECG)

4. Click **Start Acquisition** to begin collecting data

5. Monitor the live ECG signal on the chart and device status in the status panel

6. Click **Stop Acquisition** when you want to end data collection

7. Your recording is automatically saved as a CSV file and appears in the **Recordings** section

8. Click **Download** on any recording to save it to your computer

## Troubleshooting

### Connection Issues

- Ensure BITalino is powered on and paired
- Verify the MAC address is correct
- Check Bluetooth is enabled
- Try re-pairing the device

### No Data Displayed

- Confirm ECG sensor is properly connected to A1 input
- Check sensor electrodes are attached correctly
- Verify the channel code is set to `0x01` (first channel)

### Python Version Issues

- Script tries to load appropriate PLUX API binary based on OS and Python version. Please ensure correct version is used.

## Architecture

### Backend (app.py)

- **Flask**: Web server framework
- **Flask-SocketIO**: WebSocket support for real-time communication
- **PLUX API**: BITalino device communication. Binaries downloaded from [PLUX BITalino Python samples](https://github.com/pluxbiosignals/python-samples) GitHub
- **Threading**: Background acquisition without blocking web server

### Frontend (templates/index.html)

- **Chart.js**: Real-time signal visualization
- **Socket.IO Client**: WebSocket communication
- **Responsive Design**: Works on desktop and mobile browsers

### Data Flow

1. User clicks "Start Acquisition" in web interface
2. Frontend sends parameters via WebSocket to backend
3. Backend initializes BITalino device and starts acquisition
4. `onRawFrame()` callback receives data from device
5. Data is queued and broadcast to all connected web clients
6. Frontend updates chart in real-time

## CSV File Format

Recordings are saved in CSV format with the following structure:

```csv
# BITalino ECG Recording
# Start Time,2025-11-21 18:30:45
# Frequency (Hz),1000
# Channel Code,0x01
# Battery (%),95
# Device Address,98:D3:C1:FD:ED:B7
# Total Samples,12500

Sequence,ECG Value,Timestamp
0,512,1700589045.123
1,515,1700589045.124
2,518,1700589045.125
...
```

The CSV includes:

- **Metadata header**: Recording parameters and device info
- **Data columns**:
  - `Sequence`: Sample sequence number
  - `ECG Value`: Raw ADC value (0-1023 for 10-bit)
  - `Timestamp`: Unix timestamp with milliseconds

## Project Structure

```
bitalino_app/
├── app.py                          # Main application entry point
├── config/
│   ├── __init__.py
│   └── settings.py                 # Application configuration
├── models/
│   ├── __init__.py
│   └── device.py                   # BITalino device and status models
├── services/
│   ├── __init__.py
│   ├── acquisition_service.py      # Data acquisition management
│   └── recording_service.py        # CSV recording management
├── routes/
│   ├── __init__.py
│   ├── api_routes.py              # REST API endpoints
│   └── socketio_handlers.py       # WebSocket event handlers
├── utils/
│   ├── __init__.py
│   └── plux_loader.py             # Dynamic PLUX library loader
├── templates/
│   └── index.html                 # Web interface
├── recordings/                    # Saved ECG recordings (auto-created)
└── PLUX-API-Python3/              # PLUX binary files
    ├── Linux64/
    ├── LinuxARM64_*/
    ├── M1_311/
    ├── MacOS/
    │   ├── Intel310/
    │   └── ...
    ├── Win64_*/
    └── ...
```

## Future Enhancements

This MVP can be extended to support:

- Multiple sensor channels simultaneously
- Data export (CSV, JSON formats)
- Real-time signal processing (filtering, peak detection)
- Integration with Tobii Pro Glasses 3 eye tracker
- Integration with SCANeR driving simulator
- Multi-device synchronization
- Database storage for historical data
- Advanced visualization (FFT, spectrograms)
- User authentication and session management

## Technical Notes

- The app uses `threading` for concurrent acquisition and web serving
- Data queue size is limited to 1000 samples to prevent memory issues
- Chart displays last 1000 data points for optimal performance
- WebSocket messages are broadcast to all connected clients
- Battery level is queried once at acquisition start

## License

Based on [PLUX BITalino Python samples](https://github.com/pluxbiosignals/python-samples). Check PLUX licensing for API usage.

## Support

For BITalino hardware support, visit: https://www.pluxbiosignals.com/
For PLUX API documentation: Check PLUX-API-Python3 directory

---

**Part of Master's Thesis**: Platform for collecting and synchronizing physiological signals from multiple sensor systems
