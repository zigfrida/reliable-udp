import asyncio
import random
from datetime import datetime, timedelta
from packet_statistics import PacketStatistics
import socket
import sys
import signal
import time
from threading import Thread

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 65432
CLIENT_HOST = "192.168.0.2"
CLIENT_PORT = 65432

SIZE = 1024
FORMAT = "utf-8"

client_socket = None
proxy_socket = None

seq_number_with_ack_received = set()
stats = PacketStatistics()

TIMEOUT_IN_SECOND = 3
ACK_CHECKING_FREQUENCY_IN_SECOND = 1


def signal_handler(sig, frame):
    print("\nUser Interruption. Stopping Client.")
    if proxy_socket:
        proxy_socket.close()
    if client_socket:
        client_socket.close()
    exit(0)


def get_is_packet_acknowledged(seq_number: int) -> bool:
    if seq_number in seq_number_with_ack_received:
        return True
    time.sleep(ACK_CHECKING_FREQUENCY_IN_SECOND)
    return False


def get_seq_number():
    return random.randint(1, 1000)


def get_timeout():
    now = datetime.now()
    timeout = now + timedelta(seconds=TIMEOUT_IN_SECOND)
    return timeout


def send_packet(data: str, seq: int):
    print('Sending packet')
    message_with_seq = f"{data}!{seq}!{CLIENT_HOST}:{CLIENT_PORT}"
    proxy_socket.sendto(message_with_seq.encode(FORMAT), (PROXY_HOST, int(PROXY_PORT)))
    stats.increment_data_packets()
    print(stats)

def send_input():
    # Clears all acks in the memory per input.
    seq_number_with_ack_received.clear()

    input_text = input("Type words to send: ")
    seq_number = get_seq_number()
    send_packet(input_text, seq_number)
    timeout = get_timeout()

    while not get_is_packet_acknowledged(seq_number):
        if timeout <= datetime.now():
            timeout = get_timeout()
            print("Timed out")
            send_packet(input_text, seq_number)

def listen_acks():
    seq_number_with_ack_received.add(1)
    while True:
        data, _ = client_socket.recvfrom(SIZE)  # data, address
        if data:
            seq_received = data.decode(FORMAT)
            print(f"Received: {seq_received}")
            stats.increment_ack_packets()
            seq_number_with_ack_received.add(int(seq_received))
            print(stats)


def start_sending():
    try:
        while True:
            send_input()
    finally:
        proxy_socket.close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) < 2:
        print("Missing IP address and port for proxy")
    else:
        PROXY_HOST = sys.argv[1]
        PROXY_PORT = sys.argv[2]
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print(f"Client listening on {CLIENT_HOST}:{CLIENT_PORT}")
        client_socket.bind((CLIENT_HOST, int(CLIENT_PORT)))

        listen_ack_thread = Thread(target=listen_acks)
        listen_ack_thread.start()

        send_input_thread = Thread(target=start_sending)
        send_input_thread.start()
