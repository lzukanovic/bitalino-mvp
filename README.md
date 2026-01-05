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
  - Adjustable sample frequency (1-8000 Hz)

## Prerequisites

- Python 3.11+ (tested on Mac M1)
- PLUX BITalino device
- ECG sensor connected to analog input A1
- macOS, Linux, or Windows

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

- This MVP requires Python 3.11 for Mac M1 systems
- The PLUX-API-Python3/M1_311 directory contains the appropriate binaries
- For other systems, the app will automatically select the correct binary

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
bitalino-mvp/
├── app.py                      # Flask backend server
├── templates/
│   └── index.html             # Web interface
├── static/                    # (for future CSS/JS files)
├── recordings/                # Saved CSV recordings
├── PLUX-API-Python3/          # PLUX API binaries
│   ├── M1_311/               # Mac M1 Python 3.11
│   ├── Linux64/              # Linux 64-bit
│   ├── Win64_*/              # Windows binaries
│   └── ...
├── requirements.txt           # Python dependencies
└── README.md                  # This file
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
