#!/usr/bin/env python3

__version__ = '0.7'

import socket
import pickle
import struct
import threading

HOST = '' # The server's hostname or IP address
PORT = 65432       # The port on which the server is listening
MAGIC = 'dalyinskimagicpkt'

class DalyinskiClient:
    def __init__(self):
        self.buf = b''
        # find out the ip address of the server
        global HOST
        if not HOST:
            self.sudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create udp socket
            self.sudp.bind(('', PORT))
            while True:
                self.data, self.addr = self.sudp.recvfrom(1024) # wait for packet
                if self.data.startswith(MAGIC.encode()):
                    HOST = self.data[len(MAGIC):]
                    print(f"Received announcement from server {HOST.decode('utf-8')}")
                    break

        # run below if we already have ip address i.e. HOST is not empty
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))

    def command(self, cmd):
        self.s.send(cmd)
        self.data = self.s.recv(1024)
        print('Received', self.data.decode("utf-8"))

    def recv_thumb_list(self, cmd):
        ''' Adapted from here
        https://stackoverflow.com/questions/42459499/what-is-the-proper-way-of-sending-a-large-amount-of-data-over-sockets-in-python

        First unpack the first message sent by the server which contains the total
        length in bytes of the message. This is 4 byte as per struct.unpact "!I" 
        format specifier (check python struct docs).
        Then, in while loop, continue reading from the socket at most 4096 bytes,
        appending to the bytes_recvd until the whole message has been received. 
        '''

        self.s.send(cmd)
        bs = self.s.recv(4)
        msg_length, = struct.unpack('!I', bs)
        bytes_rcvd = b''
        while len(bytes_rcvd) < msg_length:
            to_read = msg_length - len(bytes_rcvd)
            print("Bytes to read: ", to_read)
            print("Bytes already read: ", len(bytes_rcvd))
            bytes_rcvd += self.s.recv(4096 if to_read > 4096 else to_read)

        print("Received a total of ", len(bytes_rcvd), " bytes")
        thumbs_lst = pickle.loads(bytes_rcvd)
        # print('[---] Thumbnail list received ', thumbs_lst)
        return thumbs_lst

