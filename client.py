import asyncio
import random
from datetime import datetime, timedelta
from packet_statistics import PacketStatistics
import socket
import sys
import signal
import threading
import logging
import time

PROXY_HOST = "127.0.0.1"  
PROXY_PORT = 65432   
CLIENT_HOST = "127.0.0.1"  
CLIENT_PORT = 65436   

SIZE = 1024
FORMAT = "utf-8"

client_socket = None
proxy_socket = None

loop = asyncio.get_event_loop()

seq_number_with_ack_received = set()
TIMEOUT_IN_SECOND = 3
ACK_CHECKING_FREQUENCY_IN_SECOND = 1

def signal_handler(sig, frame):
    print("\nUser Interruption. Stopping Client.")
    if proxy_socket:
        proxy_socket.close()
    if client_socket:
        client_socket.close()
    exit(0)

def simulate_getting_ack_back_with_possible_loss_and_delay(seq_number: int, stats: PacketStatistics):
    if random.random() < 0.2:
        print("Act for " + str(seq_number) + " received.")
        seq_number_with_ack_received.add(seq_number)
        stats.increment_ack_packets()


async def get_is_packet_acknowledged(seq_number: int) -> bool:
    await asyncio.sleep(ACK_CHECKING_FREQUENCY_IN_SECOND)
    print("Waited " + str(ACK_CHECKING_FREQUENCY_IN_SECOND) + " seconds.")
    if seq_number in seq_number_with_ack_received:
        return True
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

async def send_input(stats: PacketStatistics):
    # Clears all acks in the memory per input.
    seq_number_with_ack_received.clear()

    input_text = input("Type words to send: ")
    seq_number = get_seq_number()
    send_packet(input_text, seq_number)
    timeout = get_timeout()

    while not await get_is_packet_acknowledged(seq_number):
        if timeout <= datetime.now():
            timeout = get_timeout()
            print("Timed out")
            send_packet(input_text, seq_number)

def listen_acks():
    while True:
        data, _ = client_socket.recvfrom(SIZE) # data, address
        seq_received, addr = data.decode(FORMAT).split("!")
        print(f"Received: {seq_received}")
        seq_number_with_ack_received.add(int(seq_received))


async def main():
    global PROXY_HOST, PROXY_PORT, proxy_socket, client_socket
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

        try:
            stats = PacketStatistics()
            while True:
                await send_input(stats)
                print(stats)
        finally:
            proxy_socket.close()

asyncio.run(main())
# asyncio.run(listen_acks())