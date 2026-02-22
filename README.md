# BITalino MVP

A web-based platform for real-time physiological signal acquisition and visualization using the PLUX BITalino system.

## Features

- **Real-time Visualization**: Live chart displaying signals from BITalino analog input channels
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
- **Configurable Acquisition**:
  - Custom device MAC address
  - Adjustable sample frequency
  - Per-channel configuration for up to 6 analog inputs

## Hardware

PLUX BITalino (r)evolution standalone board:
| Ports | Resolution |
|-------|------------|
| A1 – A4 | 10-bit ADC |
| A5 – A6 | 6-bit ADC |

Supported sampling rates: **1, 10, 100, 1000 Hz**

## Prerequisites

- Python 3.11 (tested on macOS M1)
- PLUX BITalino device paired over Bluetooth
- Sensors connected to the analog inputs you intend to use

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
3. Device is paired (MAC address default: `98:D3:C1:FD:ED:B7`). Bluetooth pairing code is `1234`.

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
- **Frequency**: Set sampling rate (1, 10, 100, 1000 Hz)
- **Channels**: Configure which analog channels to acquire (A1-A6)

4. Click **Start Acquisition** to begin collecting data

5. Monitor the live ECG signal on the chart and device status in the status panel

6. Click **Stop Acquisition** when you want to end data collection

7. Your recording is automatically saved as a CSV file and appears in the **Recordings** section

8. Click **Download** on any recording to save it to your computer

## Architecture

### Backend (app.py)

- **Flask**: Web server framework
- **Flask-SocketIO**: WebSocket support for real-time communication
- **PLUX API**: BITalino device communication. Binaries downloaded from [PLUX BITalino Python samples](https://github.com/pluxbiosignals/python-samples) GitHub
- **Threading**: Background acquisition without blocking web server

### Frontend (templates/index.html)

- **Chart.js**: Real-time signal visualization
- **Toastify-js**: User notifications for status updates and errors
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

Recordings are saved to the `recordings/` directory with timestamped filenames (`recording_YYYYMMDD_HHMMSS.csv`).

```csv
# BITalino Recording
# Start Time,2026-02-22 14:30:00
# Frequency (Hz),1000
# Active Ports,1,3
# Battery (%),87
# Device Address,98:D3:C1:FD:ED:B7
# Total Samples,12500
Sequence,Timestamp,ECG (ECG) Port1,GSR (EDA) Port3
0,1740228600.123,512,318
1,1740228600.124,515,320
...
```

Column headers follow the pattern `<label> (<type>) Port<n>` for each active channel.

## Project Structure

```
bitalino_app/
├── app.py                          # Main application entry point
├── config/
│   └── settings.py                 # Application configuration
├── models/
│   └── device.py                   # BITalino device and status models
├── services/
│   ├── acquisition_service.py      # Data acquisition management
│   └── recording_service.py        # CSV recording management
├── routes/
│   ├── api_routes.py              # REST API endpoints
│   └── socketio_handlers.py       # WebSocket event handlers
├── utils/
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
For PLUX API documentation, visit: https://www.downloads.plux.info/apis/PLUX-API-Python-Docs/index.html

---

**Part of Master's Thesis**: Platform for collecting and synchronizing physiological signals from multiple sensor systems
