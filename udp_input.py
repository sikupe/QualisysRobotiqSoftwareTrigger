import socket
import array


def send_udp(host, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Send message:", message.encode("utf-8"))
    sock.sendto(message.encode("utf-8"), (host, port))
