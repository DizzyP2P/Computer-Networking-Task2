task2 简单的报文rtt测试 以及对tcp连接建立和取消的简单模拟

usage: client.py [-h] [-m MESSAGES] [-p PORT] [-r RETRIES] [-v] [-cr CRETRIES]

Simple udp client of simple imitation of tcp on udp with rtt statistic

optional arguments:
  -h, --help            show this help message and exit
  -m MESSAGES, --messages MESSAGES
                        Set the num of messages to send
  -p PORT, --port PORT  Set the port of the server(default 12345)
  -r RETRIES, --retries RETRIES
                        Set the num of retries after loss
  -v, --verbose         With more content of messages
  -cr CRETRIES, --cretries CRETRIES
                        Set the num of retries after loss of request about connection

usage: server.py [-h] [-p PORT] [-d DROPPOS] [-l [LOG]]

Simple udp server of simple imitation of tcp on udp

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Set the port of the server(default 12345)
  -d DROPPOS, --dropPos DROPPOS
                        Set the drop posibility of the received message(default 0.2)
  -l [LOG], --log [LOG]
                        Set the log file. If not set the file name, use Server.log