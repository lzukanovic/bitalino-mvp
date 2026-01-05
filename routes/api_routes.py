"""
API routes for device status and recording management.
"""
from flask import Blueprint, jsonify, send_file
from services.recording_service import list_recordings, get_recording_path

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Will be set by main app
acquisition_service = None


def init_routes(acq_service):
    """
    Initialize routes with acquisition service.
    
    Args:
        acq_service: AcquisitionService instance
    """
    global acquisition_service
    acquisition_service = acq_service


@api_bp.route('/status')
def get_status():
    """Get current device status."""
    return jsonify(acquisition_service.get_status())


@api_bp.route('/recordings')
def get_recordings():
    """List all available recordings."""
    recordings = list_recordings()
    return jsonify(recordings)


@api_bp.route('/recordings/<filename>')
def download_recording(filename):
    """
    Download a specific recording.
    
    Args:
        filename: Name of the recording file
    
    Returns:
        File download response or 404 error
    """
    filepath = get_recording_path(filename)

    if not filepath:
        return jsonify({'error': 'Recording not found'}), 404

    return send_file(filepath, as_attachment=True, download_name=filename)
