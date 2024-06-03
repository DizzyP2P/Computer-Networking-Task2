import socket
import random
import time
import struct
import argparse
from datetime import datetime
MAX_MESSAGE_LENGTH = 203
BUFFER_LENGTH = 300
VERSION = 2
SYN = 0
SYN_ACK = 1
ACK = 2
FIN = 3
FIN_ACK = 4
NORMAL_DATA = 5
DROP_POS = 0.2
UNCONNECTED = 0
CONNECTED = 1
DISCONNECTED = 2
DEBUG = 1

typeToStr = {0:"SYN",1:"SYN_ACK",2:"ACK",3:"FIN",4:"FIN_ACK",5:"NORMAL_DATA"}
receive_protocol_format = 'hBB199s'
send_protocol_format = 'hBBd191s'

def check_port_in_use(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def pack_message(seq_no, msg_type,payload=b''):
    payload_bytes = payload.encode('utf-8') if isinstance(payload, str) else payload
    return struct.pack(send_protocol_format, seq_no, VERSION, msg_type,time.time(),payload_bytes.ljust(191, b'\0'))

def unpack_message(data):
    seq_no, version, msg_type,payload = struct.unpack(receive_protocol_format, data)
    return seq_no, version, msg_type,payload.rstrip(b'\0')

def printMessage(M,addr):
    print(f'[{datetime.now()}] Received: seq.No:{M[0]} type:{typeToStr[M[2]]} from {addr}')

class Connection:
    def __init__(self,sock,addr) -> None:
        self.addr = addr
        self.connected = UNCONNECTED
        self.sock = sock

    def send_packet(self, seq_no,msg_type, payload=b''):
        message = pack_message(seq_no, msg_type, payload)
        print(f'[{datetime.now()}]:Sended: seq.No:{seq_no} type:{typeToStr[msg_type]} to {self.addr}')
        self.sock.sendto(message, self.addr)

    def handle_message(self,response):
        if(response[2] == SYN):
            self.send_packet(0,SYN_ACK)
            print(f"Connection succeed with {self.addr}")
            self.connected = CONNECTED 
        elif(response[2] == FIN):
            self.send_packet(0,FIN_ACK)
            print(f"Disconnected successfully with {self.addr}")
            self.connected = DISCONNECTED
        elif(response[2]==NORMAL_DATA):
            self.send_packet(response[0],NORMAL_DATA)
        return self.connected

class Udp_server:
    def __init__(self,host,port) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        self.ConnectionList = {}
        print(f"[{datetime.now()}]:Server started at {host}:{port}")

    def BuildConnection(self,addr):
        self.ConnectionList[addr] = Connection(self.server_socket,addr)

    def receive_packet(self):
        try:
            data, addr= self.server_socket.recvfrom(BUFFER_LENGTH)
            return unpack_message(data),addr
        except socket.timeout:
            return None
    def run(self):
        while True:
            data,addr = self.receive_packet()
            if(data):
                printMessage(data,addr)
                if random.random()>DROP_POS:  
                    if(addr not in self.ConnectionList):
                        self.BuildConnection(addr)
                    if(self.ConnectionList[addr].handle_message(data)==DISCONNECTED):
                        self.ConnectionList.pop(addr)
                else:
                    print("drop!");
 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple udp server of simple imitation of tcp on udp')
    parser.add_argument("-p","--port",type=int,default=12345,help="Set the port of the server(default 12345)")
    parser.add_argument("-d","--dropPos",type=float,default=0.2,help="Set the drop posibility of the received message(default 0.2)")
    args = parser.parse_args()
    DROP_POS = args.dropPos
    if(DROP_POS<0 or DROP_POS>1):
        print("Error: Drop pos not in range (0-1)")
        exit(22)
    if(args.port<1024 or args.port >65535):
        print("Error: Port num not in range (1024-65535)")
        exit(22)

    if check_port_in_use(args.port):
        print(f"Error: Port {args.port} is in use")
        exit(22)

    server = Udp_server("127.0.0.1", args.port)
    server.run()