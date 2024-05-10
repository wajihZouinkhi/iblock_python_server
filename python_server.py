import logging
import threading

import socketio
import time
import serial


ser = serial.Serial('COM3', 115200, timeout=1)

# command received of type list
def send_command(commands):
    ser.write(commands.encode())
            
            
# Initialize and configure logging
logging.basicConfig(
    format='[%(asctime)s] [%(name)s] [%(funcName)s] [%(levelname)s] %(message)s')
logger = logging.getLogger('test_python_socketio_auth')
logger.setLevel(logging.INFO)

sio = socketio.Client(reconnection=True)

# Initialize event which is used to signal that a server response has been received
server_response_received = threading.Event()

@sio.on('connect', namespace='/robot')
def on_connect():
    while True:
        response = ser.readline().strip().decode('utf-8')
        if response == "Ready":
            print("Arduino is ready.")
            break
    logger.info('Connected to Socket.IO server')


@sio.on('disconnect',namespace='/robot')
def on_disconnect():
    logger.info('Disconnected from Socket.IO server')


@sio.on('message', namespace='/robot')
def on_message(data):
    logger.info('Message received: %s', data)
    messages.append(data)
    
@sio.on('robotData', namespace='/robot')
def on_message_data(data):
    print('Received messageData event:', data)  # Debugging print statement
    send_command(data['commands'])
    
    
# Try to establish a connection
sio.connect("http://localhost:3005/", namespaces=['/robot'])

# Keep the script running indefinitely to listen for events
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt detected. Exiting.')
        break


