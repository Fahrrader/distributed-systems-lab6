#!/usr/bin/env python3
import sys
import os
import socket
from re import match


def client():
    if len(sys.argv) != 4:
        print("Excuse me, you have to send the following arguments: "
              "file name, IP-address or domain name, and port number.")
        return

    s = socket.socket()
    s.connect((sys.argv[2], int(sys.argv[3])))

    f = open(sys.argv[1], "rb")
    file_size = os.fstat(f.fileno()).st_size

    s.send(str.encode(sys.argv[1], 'utf-8'))

    chunk_size = 1024
    percent = 1
    sent = 0
    l = f.read(chunk_size)
    while l:
        s.send(l)
        if sent / file_size * 100 > percent:
            print(percent, '%')
            percent += 4  # ceil(sent / file_size * 100)
        sent += chunk_size
        l = f.read(chunk_size)
    print("exit")
    f.close()


if __name__ == "__main__":
    client()
