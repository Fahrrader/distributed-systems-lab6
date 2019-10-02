#!/usr/bin/env python3
import types
import socket
import selectors
import os
from re import match
from threading import Thread


host = ''
port = 8800
clients = []


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # add 'me> ' to sended message
    def _clear_echo(self, data):
        # \033[F – symbol to move the cursor at the beginning of current line (Ctrl+A)
        # \033[K – symbol to clear everything till the end of current line (Ctrl+K)
        self.sock.sendall('\033[F\033[K'.encode())
        data = 'me> '.encode() + data
        # send the message back to user
        self.sock.sendall(data)

    # broadcast the message with name prefix eg: 'u1> '
    def _broadcast(self, data):
        data = (self.name + '> ').encode() + data
        for u in clients:
            # send to everyone except current client
            if u == self.sock:
                continue
            u.sendall(data)

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        # accept file name, create file with this name, create a copy, if already exists
        file_name = self.sock.recv(1024).decode("utf-8")
        if os.path.exists(file_name):
            i = file_name.rfind('.')
            copies = [f for f in os.listdir('.') if
                      f.startswith(file_name[:i] + '(') and f.endswith(')' + file_name[i:])
                      and match(r"[0-9]+", f[f.rfind('(') + 1:f.rfind(')')])]
            max_copy = max(copies) if copies else '(1)'
            file_name = (file_name[:i] + '(%s)' + file_name[i:]) % \
                        (int(max_copy[max_copy.rfind('(') + 1:max_copy.rfind(')')]) + 1)

        f = open(file_name, 'wb')
        while True:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            data = self.sock.recv(1024)
            if not data:
                # if we got no data – client has disconnected
                f.close()
                self._close()
                # finish the thread
                return
            f.write(data)


def server():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind((host, port))
    sock.listen()
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    server()
