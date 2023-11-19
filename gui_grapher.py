import matplotlib.pyplot as plt
import numpy as np

sender_ack_from_receiver_total_packet = 0
sender_data_to_receiver_total_packet = 0

proxy_ack_to_sender_total_packet = 0
proxy_act_from_receiver_total_packet = 0
proxy_data_from_sender_total_packet = 0
proxy_data_to_receiver_total_packet = 0

receiver_act_to_sender_total_packet = 0
receiver_data_from_sender_total_packet = 0


def get_total_packet_data():
    return (
        sender_ack_from_receiver_total_packet,
        sender_data_to_receiver_total_packet,
        proxy_ack_to_sender_total_packet,
        proxy_act_from_receiver_total_packet,
        proxy_data_from_sender_total_packet,
        proxy_data_to_receiver_total_packet,
        receiver_act_to_sender_total_packet,
        receiver_data_from_sender_total_packet
    )


x = np.linspace(0, 2 * np.pi, 400)
y = np.sin(x ** 2)

fig, axs = plt.subplots(4, 2)
axs[0, 0].plot(x, y)
axs[0, 0].set_title("Sender: Total of data packets sent")
axs[0, 1].plot(x, y ** 2)
axs[0, 1].set_title("Proxy: Total of data packets received")

axs[1, 0].plot(x + 1, y + 1)
axs[1, 0].set_title("Proxy: Total of data packets sent")
axs[1, 1].plot(x + 2, y + 2)
axs[1, 1].set_title("Receiver: Total of data packets received")

axs[2, 0].plot(x, y)
axs[2, 0].set_title("Receiver: Total of ack packets sent")
axs[2, 1].plot(x, y)
axs[2, 1].set_title("Proxy: Total of ack packets received")

axs[3, 0].plot(x, y)
axs[3, 0].set_title("Proxy: Total of ack packets sent")
axs[3, 1].plot(x, y ** 2)
axs[3, 1].set_title("Sender: Total of ack packets received")

fig.tight_layout()
plt.show()
plt.show
