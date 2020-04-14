import socket
import sys
import struct
from threading import Thread

MULTICAST_TTL = 2

class Sender(Thread):
    def __init__(self, ip, port, cast_type):
        Thread.__init__(self)
        self.cast = cast_type
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        if cast_type == '-m':
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
        elif cast_type == '-b':
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
    def run(self):
        while True:
            MESSAGE = str(input('> '))
            self.sock.sendto(bytes(MESSAGE, encoding='utf-8'), (self.UDP_IP, self.UDP_PORT))
            

class Receiver(Thread):
    def __init__(self, ip, port, cast_type):
        Thread.__init__(self)
        self.cast = cast_type
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
        
        if cast_type == '-m':
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
            #self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
            mreq = struct.pack("4sl", socket.inet_aton(self.UDP_IP), socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        elif cast_type == '-b':
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
        
    def run(self):
        self.sock.bind((self.UDP_IP, self.UDP_PORT))

        while True:
            data, addr = self.sock.recvfrom(1024) 
            print("received message:", str(data, encoding='utf-8'))


def unicast_threads(source, direction, cast_type):
    udp_sender = Sender(direction, 5000 + int(direction.split('.')[-1], 10), cast_type)
    udp_sender.start()
    udp_receiver = Receiver(source, 5000 + int(source.split('.')[-1], 10), cast_type)
    udp_receiver.start()


def multicast_threads(multicast_group, multicast_port, cast_type):
    udp_sender = Sender(multicast_group, int(multicast_port, 10), cast_type)
    udp_sender.start()
    udp_receiver = Receiver(multicast_group, int(multicast_port, 10), cast_type)
    udp_receiver.start()


def broadcast_threads(source_port, direction_port, cast_type):
    udp_sender = Sender('255.255.255.255', int(direction_port, 10), cast_type)
    udp_sender.start()
    udp_receiver = Receiver('', int(source_port, 10), cast_type)
    udp_receiver.start()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == '-u':
            source = str(input('Enter your ip: '))
            direction = str(input('Enter destination ip: '))
            unicast_threads(source, direction, sys.argv[1])
        elif sys.argv[1] == '-m':
            multicast_group = str(input('Enter your multicast group: '))
            multicast_port = str(input('Enter your port: '))
            #direction = str(input('Enter destination ip: '))
            #direction_port = str(input('Enter destination port: '))
            multicast_threads(multicast_group, multicast_port, sys.argv[1])
        elif sys.argv[1] == '-b':
            source_port = str(input('Enter your port: '))
            direction_port = str(input('Enter destination port: '))
            broadcast_threads(source_port, direction_port, sys.argv[1])
        else:
            print('Wrong arg. exit')
            
    else:
        print("Usage: python3 <program> (-u|-m|-b)")
        print("Use -u for unicast messenger")
        print("Use -m for multicast messenger")
        print("Use -b for broadcast messenger")
