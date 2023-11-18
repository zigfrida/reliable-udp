import socket
import signal
import sys

HOST = "127.0.0.1"  
PORT = 65432       
SIZE = 1024
FORMAT = "utf-8"

server_socket = None

def signal_handler(sig, frame):
    print("\nUser Interruption. Shutting down server.")
    if server_socket: 
        server_socket.close()
    exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, int(PORT)))
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        message_with_seq, addr = server_socket.recvfrom(SIZE) 
        if message_with_seq:
            data, seq, client_addr = message_with_seq.decode(FORMAT).split("!")
            print(f"Message Received: {data}")
            server_response = f"{seq}!{client_addr}"
            print(f"Sending ACK: {seq}")

            server_socket.sendto(server_response.encode(FORMAT), addr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing IP or port.")
    else:
        HOST = sys.argv[1]
        PORT = sys.argv[2]
        main()