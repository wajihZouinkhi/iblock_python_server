import logging
import threading
import time
import serial
import serial.tools.list_ports
import socketio
from aiohttp import web

class RobotConnector:
    def __init__(self, baud_rate=115200, websocket_port=3002, namespace='/robot'):
        self.baud_rate = baud_rate
        self.websocket_port = websocket_port
        self.namespace = namespace
        self.ser = None
        self.sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
        self.app = web.Application()
        self.sio.attach(self.app)
        self._setup_logging()
        self._setup_socketio_events()

    def _setup_logging(self):
        logging.basicConfig(
            format='[%(asctime)s] [%(name)s] [%(funcName)s] [%(levelname)s] %(message)s')
        self.logger = logging.getLogger('RobotConnector')
        self.logger.setLevel(logging.INFO)

    def _setup_socketio_events(self):
        self.sio.on('connect', self.on_connect, namespace=self.namespace)
        self.sio.on('disconnect', self.on_disconnect, namespace=self.namespace)
        self.sio.on('message', self.on_message, namespace=self.namespace)
        self.sio.on('robotData', self.on_robot_data, namespace=self.namespace)
        
    def find_serial_port(self):
        ports = list(serial.tools.list_ports.comports())
        if ports:
            return ports[0].device
        else:
            return None

    def connect_serial(self):
        while not self.ser:
            serial_port = self.find_serial_port()
            if serial_port:
                try:
                    self.ser = serial.Serial(serial_port, self.baud_rate, timeout=1)
                    self.logger.info('Connected to serial port %s', serial_port)
                    self.wait_for_arduino_ready()
                except serial.SerialException as e:
                    self.logger.error('Failed to connect to serial port: %s', e)
                    self.ser = None
            else:
                self.logger.info('No serial device found. Please attach a device.')
                time.sleep(5)  # Wait for a few seconds before retrying

    def wait_for_arduino_ready(self):
        while True:
            response = self.ser.readline().strip().decode('utf-8')
            if response == "Ready":
                self.logger.info("Arduino is ready.")
                break

    def send_command(self, commands):
        if self.ser:
            self.ser.write(commands.encode())
    
    def on_connect(self, sid, environ):
        self.logger.info('Connected to Socket.IO server')

    def on_disconnect(self, sid):
        self.logger.info('Disconnected from Socket.IO server')

    def on_message(self, sid, data):
        self.logger.info('Message received: %s', data)

    def on_robot_data(self, sid, data):
        self.logger.info('Received robotData event: %s', data)
        print(data)
        self.send_command(data["commands"])
    def run(self):
        self.connect_serial()
        if self.ser:
            self.logger.info('Starting Socket.IO server on port %d', self.websocket_port)
            web.run_app(self.app, port=self.websocket_port)

    
    
if __name__ == "__main__":
    robot_connector = RobotConnector()
    robot_connector.run()