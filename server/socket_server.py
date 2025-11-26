import socket
import json
import random
import time

HOST = "0.0.0.0"  
PORT = 9999      

def generate_sensor_data():
    """Generate random sensor data."""
    return {
        "Device_ID": random.randint(1000, 9999),
        "Battery_Level": round(random.uniform(2.5, 4.2), 2),
        "Temperature": round(random.uniform(20, 40), 2),
        "Humidity": round(random.uniform(30, 80), 2),
        "Route_From": random.choice(["Chennai", "Delhi", "Mumbai"]),
        "Route_To": random.choice(["London", "Paris", "Tokyo"]),
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

def start_socket_server():
    """Simple TCP socket server that streams JSON data."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"Socket Server listening on {HOST}:{PORT}")

    conn, addr = server.accept()
    print(f"Connected by {addr}")

    while True:
        try:
            data = generate_sensor_data()
            conn.sendall(json.dumps(data).encode("utf-8"))
            print(f"Sent: {data}")
            time.sleep(2)
        except (BrokenPipeError, ConnectionResetError):
            print("Connection lost. Waiting for reconnection...")
            conn, addr = server.accept()
            print(f"Reconnected by {addr}")

if __name__ == "__main__":
    print("Starting basic socket data server...")
    start_socket_server()
