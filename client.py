#!/usr/bin/env python3

import socket


class RemofoyClient:
    def __init__(self):
        HOST = '192.168.99.2' # The server's hostname or IP address
        PORT = 65432       # The port on which the server is listening
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))

    def command(self, cmd):
        self.s.send(cmd)
        self.data = self.s.recv(1024)
        print('Received', self.data.decode("utf-8"))


