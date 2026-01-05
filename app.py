"""
BITalino MVP Flask Application
Main application entry point with SocketIO for real-time data streaming.
"""
import threading
import time
from queue import Queue
from flask import Flask, render_template
from flask_socketio import SocketIO

# Import configuration
from config.settings import (
    SECRET_KEY, HOST, PORT, DEBUG,
    SOCKETIO_CORS_ALLOWED_ORIGINS, SOCKETIO_ASYNC_MODE,
    DATA_QUEUE_MAX_SIZE
)

# Import services
from services.acquisition_service import AcquisitionService

# Import routes
from routes.api_routes import api_bp, init_routes
from routes.socketio_handlers import init_socketio_handlers


def create_app():
    """
    Create and configure Flask application.
    
    Returns:
        tuple: (Flask app, SocketIO instance)
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY

    # Initialize SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins=SOCKETIO_CORS_ALLOWED_ORIGINS,
        async_mode=SOCKETIO_ASYNC_MODE
    )

    # Create data queue for real-time streaming
    data_queue = Queue(maxsize=DATA_QUEUE_MAX_SIZE)

    # Initialize acquisition service
    acquisition_service = AcquisitionService(data_queue, socketio)

    # Initialize routes with services
    init_routes(acquisition_service)
    init_socketio_handlers(socketio, acquisition_service)

    # Register blueprints
    app.register_blueprint(api_bp)

    # Main route
    @app.route('/')
    def index():
        """Serve the main web interface."""
        return render_template('index.html')

    # Start data broadcast worker
    def data_broadcast_worker():
        """Background worker to broadcast data to all connected clients."""
        while True:
            if not data_queue.empty():
                # Get data from queue
                data = data_queue.get()
                # Broadcast to all connected clients
                socketio.emit('new_data', data)
            else:
                # Small sleep to prevent busy waiting
                time.sleep(0.001)

    broadcast_thread = threading.Thread(target=data_broadcast_worker, daemon=True)
    broadcast_thread.start()

    return app, socketio

if __name__ == '__main__':
    print("Starting BITalino MVP Server...")
    print(f"Open http://localhost:{PORT} in your browser")
    
    app, socketio = create_app()
    socketio.run(
        app,
        host=HOST,
        port=PORT,
        debug=DEBUG,
        use_reloader=False
    )
