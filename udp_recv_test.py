import socket
import threading
import signal
import struct
import argparse
import datetime

# Flag to control the server loop
running = True

def handle_client(server_socket):
    while running:
        try:
            data, addr = server_socket.recvfrom(1024)
            if data:
                unpacked_data = struct.unpack('>2d', data)
                x = unpacked_data[0]
                y = unpacked_data[1]
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received target from {addr}: (x = {x} mm, y = {y} mm)")
        except socket.timeout:
            continue

def signal_handler(sig, frame):
    global running
    print("Shutting down server...")
    running = False

def start_server(ip, port):
    global running
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (ip, port)
    server.bind(address)
    server.settimeout(1.0)
    print(f"Server listening on {address}...")

    client_handler = threading.Thread(target=handle_client, args=(server,))
    client_handler.start()

    while running:
        pass

    server.close()
    print("Server shut down.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A python script for testing UDP communication for the capture program.')
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='The ip address to listen on.')
    parser.add_argument('--port', type=int, default=60522, help='The port number to listen on.')
    args = parser.parse_args()
    signal.signal(signal.SIGINT, signal_handler)
    start_server(args.ip, args.port)