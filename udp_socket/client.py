import socket
import time
import struct
import math

# Constants
MAX_MESSAGE_LENGTH = 203
BUFFER_LENGTH = 300
VERSION = 2
SYN = 0
SYN_ACK = 1
FIN = 3
FIN_ACK = 4
NORMAL_DATA = 5
MAX_RETRIES = 2
# Protocol formats
send_protocol_format = 'hBB199s'
receive_protocol_format = 'hBBd191s'
typeToStr = {0:"SYN",1:"SYN_ACK",2:"ACK",3:"FIN",4:"FIN_ACK",5:"NORMAL_DATA"}
def printMessage(M):
    print(f'seq.No:{M[0]} type:{typeToStr[M[2]]}')
def pack_message(seq_no, msg_type, payload=b''):
    payload_bytes = payload.encode('utf-8') if isinstance(payload, str) else payload
    return struct.pack(send_protocol_format, seq_no, VERSION, msg_type, payload_bytes.ljust(199, b'\0'))

def unpack_message(data):
    seq_no, version, msg_type,time,payload = struct.unpack(receive_protocol_format, data)
    return seq_no, version, msg_type, time,payload.rstrip(b'\0')

class UDPClient:
    def __init__(self, server_ip, server_port):
        self.server_address = (server_ip, server_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(0.1)  # Timeout for socket operations
        self.seq_no = 0  # Sequence number for packets
        self.rtt = []
        self.num_of_sended = 0  # 发送的 UDP 包总数
        self.num_of_received = 0  # 接收到的 UDP 包总数

    def send_packet(self, msg_type, payload=b''):
        message = pack_message(self.seq_no, msg_type, payload)
        self.client_socket.sendto(message, self.server_address)
        self.num_of_sended +=1

    def receive_packet(self):
        try:
            data, _ = self.client_socket.recvfrom(BUFFER_LENGTH)
            return unpack_message(data)
        except socket.timeout:
            return None

    def messageTransfer(self,msg_type,payload=b'',retries = MAX_RETRIES):
        attempt = 1
        while attempt <= retries+1:
            start = time.time()
            self.send_packet(msg_type,payload)
            response = self.receive_packet()
            end = time.time()
            if(response == None):
                attempt+=1
            else:
                self.num_of_received+=1
                self.rtt.append(end-start)
                printMessage(response)
                return response,end-start,attempt
        return (None,None,attempt-1)

    def connect(self):
        # Send SYN
        response,*_ = self.messageTransfer(SYN,retries=5)
        if(response!=None):
            if(response[2]==SYN_ACK):
                print("连接成功!")
                return True
            else:
                print("连接失败 服务器应答错误!")
        else:
            print("连接失败 服务器未应答!")
        return None;

    def disconnect(self):
        # Send FIN
        # Wait for FIN-ACK
        response,*_ = self.messageTransfer(FIN,retries=5)
        if(response!=None):
            if(response[2]==FIN_ACK):
                print("断开成功!")
                return True
            else:
                print("断开连接失败 服务器应答错误!")
        else: 
            print("断开连接失败 服务器未应答!")
        print("单方面断开连接中.....")
        return None

    def send_data(self):
        response,rtt,attempt = self.messageTransfer(NORMAL_DATA, "Hello, TCP over UDP!")
        if(response!=None):
            if(response[0]!=self.seq_no):
                print("发生未知错误")
                exit(0)
            print(f'seqNo {self.seq_no} attemp{attempt} 成功 rtt={rtt}')
        else:
            print(f'seqNo {self.seq_no} {attempt}次attemp都失败 丢包')

    def calculate_statistics(self):
            # 计算并返回所需的统计信息
            if self.num_of_sended == 0:
                return "No packets sent."

            # 计算丢包率
            loss_rate = (1 - self.num_of_received / self.num_of_sended) * 100

            # 如果没有接收到任何包，则无法计算 RTT 相关统计数据
            if not self.rtt:
                return f"Loss Rate: {loss_rate:.2f}%, No RTT data available."

            # 计算 RTT 最大值、最小值、平均值和标准差
            max_rtt = max(self.rtt)
            min_rtt = min(self.rtt)
            avg_rtt = sum(self.rtt) / len(self.rtt)
            std_rtt = math.sqrt(sum((x - avg_rtt) ** 2 for x in self.rtt) / len(self.rtt))

            return f"Loss Rate: {loss_rate:.2f}%, Max RTT: {max_rtt*1000:.5f} us, Min RTT: {min_rtt*1000:.5f} us, Average RTT: {avg_rtt*1000:.5f} us, RTT Standard Deviation: {std_rtt*1000:.5f} us"

    def run(self,messageNums):
        if(self.connect()==None):
            return None
        else:
            self.seq_no+=1
        try:
            for _ in range(messageNums):
                self.send_data()
                self.seq_no+=1
        finally:
            self.seq_no = 0
            self.disconnect()
            print(self.calculate_statistics())

if __name__ == "__main__":
    client = UDPClient("127.0.0.1", 12345)
    client.run(10)