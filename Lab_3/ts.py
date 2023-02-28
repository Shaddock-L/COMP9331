# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 17:52:48 2021

@author: Leyang Li (z5285799) for comp 9331.
"""

from socket import *
import sys

serverPort = int(sys.argv[1]) 
serverSocket = socket(AF_INET, SOCK_STREAM) #create a server socket
serverSocket.bind(('', serverPort)) #bind the port
serverSocket.listen(1) # max connection is 1

while True:
    print("Sir! I am ready to serve!")
    connectionSocket, addr = serverSocket.accept()
    
    try:
        message = connectionSocket.recv(1024)
        filename = message.split()[1]
        req_type = filename[-3:]
        if (req_type == b'png'):
            fp = open(filename[1:], 'rb')
            data = fp.read()
            connectionSocket.send('HTTP/1.1 200 OK\r\nContent-Type: image/png\r\n\r\n'.encode())
            connectionSocket.send(data)
        
        elif (req_type == b'tml'):
            fp = open(filename[1:])
            connectionSocket.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'.encode())
            data = fp.read()
            connectionSocket.send(data.encode())
        connectionSocket.close()
    except IOError:
        connectionSocket.send('HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n'.encode())
        connectionSocket.send('No such file!'.encode())
        connectionSocket.close()
serverSocket.close()
    
        