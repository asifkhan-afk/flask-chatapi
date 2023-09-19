# sockets.py

from flask_socketio import SocketIO

socketio = SocketIO(debug=True,cors_allowed_origins="*",namespace='/chat')
