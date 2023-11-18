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

HOST = "127.0.0.1"
PORT = 65432
SIZE = 1024
FORMAT = "utf-8"
server_socket = None

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

seq_number_with_ack_received = set()
TIMEOUT_IN_SECOND = 3
ACK_CHECKING_FREQUENCY_IN_SECOND = 1


def signal_handler(sig, frame):
    print("\nUser Interruption. Stopping Client.")
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


def send_packet(server_socket, data: str, seq: int):
    print('Sending packet')
    message_with_seq = f"{data}!{seq}"
    server_socket.sendto(message_with_seq.encode(FORMAT), (HOST, int(PORT)))


async def send_input(stats: PacketStatistics, server_socket):
    # Clears all acks in the memory per input.
    seq_number_with_ack_received.clear()

    input_text = input("Type words to send: ")
    seq_number = get_seq_number()
    send_packet(server_socket, input_text, seq_number)
    timeout = get_timeout()

    while not await get_is_packet_acknowledged(seq_number):
        if timeout <= datetime.now():
            timeout = get_timeout()
            print("Timed out")
            send_packet(server_socket, input_text, seq_number)


async def send_data(name):
    stats = PacketStatistics()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        await send_input(stats, server_socket)
        print(stats)


async def receive_acks(name):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.info("Thread %s: starting", name)
    print("Listening")
    while True:
        data, _ = server_socket.recvfrom(SIZE)  # data, address
        seq_received = int(data.decode(FORMAT))
        print(f"Received: {seq_received}")
        seq_number_with_ack_received.add(seq_received)


def receive_thread(args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(receive_acks(args))
    loop.close()


def send_thread(args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(send_data(args))
    loop.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing required arguments.")
        print("Command: python3 proxy.py 127.0.0.1 65432 127.0.0.1 65433")
    else:
        PROXY_HOST = sys.argv[1]
        PROXY_PORT = sys.argv[2]

    signal.signal(signal.SIGINT, signal_handler)
    logging_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")

    recv_thread = threading.Thread(target=receive_thread, args=("receive_thread",))
    recv_thread.start()
    send_thread = threading.Thread(target=send_thread, args=("send_thread",))
    send_thread.start()

