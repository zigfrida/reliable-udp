import socket
import sys
import signal
import random
import time

SIZE = 1024
FORMAT = "utf-8"

PROXY_HOST = "127.0.0.1"  
PROXY_PORT = 65431      

SERVER_HOST = "127.0.0.1" 
SERVER_PORT = 65432  

PROB_DROPS = 0.2
PROB_DELAYS = 0.3

proxy_socket = None
server_socket = None
client_addr = None
server_resposponse = None

def signal_handler(sig, frame):
    print("\nUser Interruption. Stopping Proxy.")
    if(proxy_socket):
        proxy_socket.close()
    exit(0)

# Forward message and sequence number to the server
def send_to_server():
    global client_addr, server_response
    chance = random.random() 
    if chance > PROB_DELAYS:
        print("Delay packet to Server.")
        time.sleep(3)
    elif chance > PROB_DROPS:
        print("Packet dropped, not sent to Server.")
        return

    print("Sending to server")
    client_data, adr = proxy_socket.recvfrom(SIZE)  
    client_addr = adr
    sequence_message = client_data.decode(FORMAT)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.sendto(sequence_message.encode(FORMAT), (SERVER_HOST, SERVER_PORT))

    # Receive response from the server
    seq, _ = server_socket.recvfrom(SIZE)
    server_response = seq
    server_socket.close()


def send_to_client():
    chance = random.random() 
    if chance > PROB_DELAYS:
        print("Delay packet to Client.")
        time.sleep(3)
    elif chance > PROB_DROPS:
        print("Packet dropped, not sent to Client.")
        return

    print("Sending to client.")
    proxy_socket.sendto(server_response, client_addr) # Send server's response (sequence number) back to the client


def main():
    signal.signal(signal.SIGINT, signal_handler)

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    print(f"Proxy listening on {PROXY_HOST}:{PROXY_PORT}")

    while True:
        send_to_server()
        send_to_client()

    proxy_socket.close()  # Close the proxy socket when done

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing required arguments.")
    else: 
        PROXY_HOST = sys.argv[1]
        PROXY_PORT = sys.argv[2]

        SERVER_HOST = sys.argv[3]
        SERVER_PORT = sys.argv[4]

    main()
