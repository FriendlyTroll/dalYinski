#!/usr/bin/env python3

import socket
import pickle
import struct
import threading

HOST = '' # The server's hostname or IP address
PORT = 65432       # The port on which the server is listening
MAGIC = 'dalyinskimagicpkt'

class DalyinskiClient:
    def __init__(self):
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
        ''' Keep receiving all the data sent by the
        server. '''
        self.s.send(cmd)
        packets = bytearray()
        # while True:
            # print("<<< receiving")
        packet = self.s.recv(32000)
            # if not packet: 
            #     print("BREAKING out of while")
            #     break
            # print("+++ appending")
        packets.extend(packet)
        # packets = self.recv_msg(self.s)
        # print("[][][] packets content >", packets)
        thumbs_lst = pickle.loads(packets)
        # print('[---] Thumbnail list received ', thumbs_lst)
        return thumbs_lst

