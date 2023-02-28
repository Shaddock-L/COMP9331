# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 11:00:34 2021
client.py
Assignment for COMP9331
@author: Leyang Li (z5285799)
"""
import threading
from socket import *
import sys


cli_IP = sys.argv[1]  #read the first pera as the IP address
serverPort = int(sys.argv[2]) #read the second para as the port used by the client
client_udp_server_port = sys.argv[3]

serverIP = '127.0.0.1' 
#serverPort = 11000
#client_udp_server_port = '6666'


clientSocket = socket(AF_INET, SOCK_STREAM) #creat a clientSocket 
#clientSocket.connect((serverIP, serverPort))
clientSocket.connect((serverIP, serverPort))
log_state = False
out_state = False
username = ''

def log_in(enter_username):
    global clientSocket
    global serverIP
    global serverPort
    global log_state
    global username
    global cli_IP
    print(enter_username)
    
    username = input()
    if (username):
        
        clientSocket.sendto(username.encode(), (serverIP, serverPort))
        response, serverAddress = clientSocket.recvfrom(1024)
        print(response.decode())
        password = input()
        if (password):
            clientSocket.sendto(password.encode(), (serverIP, serverPort))
            response, serverAddress = clientSocket.recvfrom(1024)
            print(response.decode())
            if (response.decode()=='Login successfully!'):
                clientSocket.sendto(client_udp_server_port.encode(), (serverIP, serverPort))
                log_state = True
                #cli_info = clientSocket.getsockname()
                cli_ipAdr = cli_IP[0]
                clientSocket.sendto(cli_ipAdr.encode(), (serverIP, serverPort)) 
        else:
            clientSocket.sendto('乱码'.encode(), (serverIP, serverPort))
            
            
    else:
        log_in('Username: ')

while(1):
    if (out_state == True):
        break
   
    response, serverAddress = clientSocket.recvfrom(1024)
    
    if (log_state == False):
        log_in('Username: ')
    else:
        if (response.decode() == 'Enter one of the commands(MSG, DLT, EDT, RDM, ATU, OUT, UPD):'):
            #print(response.decode())
            cmd = input(response.decode())
            if (cmd[:3] == 'MSG'):
                clientSocket.sendto(cmd.encode(), (serverIP, serverPort))
                # send the username
                clientSocket.sendto(username.encode(), (serverIP, serverPort))
                response, serverAddress = clientSocket.recvfrom(1024)
                if response.decode()[:5] == 'ERROR':
                    print(response.decode())
                elif (response.decode() == 'success post'):
                    continue
            elif (cmd == 'OUT'):
                clientSocket.sendto(cmd.encode(), (serverIP, serverPort))
                #send username
                clientSocket.sendto(username.encode(),(serverIP, serverPort))
                response, serverAddress = clientSocket.recvfrom(1024)
                if response.decode()[:3] == 'BYE':
                    print(response.decode())
                    out_state = True
                    
            elif (cmd[:3] == 'DLT'):
                #DLT #4 23 Feb 2021 16:01:20
                clientSocket.sendto(cmd.encode(), (serverIP, serverPort))
                #send the username
                clientSocket.sendto(username.encode(),(serverIP, serverPort))
                #check whether the dlt cmd worked  'Message' -> success  'Opps' -> fail
                response = clientSocket.recv(1024).decode()
                print(response)
                
            elif (cmd[:3] == 'EDT'):
                #EDT #3 23 Feb 2021 16:01:01 Computer Network Rocks
                clientSocket.sendto(cmd.encode(), (serverIP, serverPort))
                #send the username
                clientSocket.sendto(username.encode(),(serverIP, serverPort))
                #check whether the edt cmd worked  'Message' -> success  'Opps' -> fail
                response = clientSocket.recv(1024).decode()
                print(response)
                
            elif (cmd[:3] == 'RDM'):
                #RDM 23 Feb 2021 15:00:00
                clientSocket.sendto(cmd.encode(), (serverIP, serverPort))
                # receie the  msg numbers
                response = clientSocket.recv(1024).decode()
                if (response == '0'):
                    print('no new message')
                elif (response[0] == 'E'):
                    print(response)
                else:
                    for i in range(int(response)):
                        response = clientSocket.recv(1024).decode()
                        print(response)
            elif (cmd == 'ATU'):
                clientSocket.sendto(cmd.encode(), (serverIP, serverPort))
                #send the username
                clientSocket.sendto(username.encode(),(serverIP, serverPort))
                #check the respond number
                response = clientSocket.recv(1024).decode()
                for i in range(int(response)):
                    response = clientSocket.recv(1024).decode()
                    print(response)

                
                
            # invalid command
            else:
                clientSocket.sendto(cmd.encode(), (serverIP, serverPort))
                response = clientSocket.recv(1024)
                print(response.decode())
                
                
    
    
    
clientSocket.close()
'''   
        
################# receive the MSG, DLT, EDT, RDM, ATU, OUT, UPD cmd
response, serverAddress = clientSocket.recvfrom(1024)
next_cmd = input(response.decode()+': ')

# send the username
clientSocket.sendto(username.encode(), (serverIP, serverPort))
#check whether the MSG cmd is valid
response, serverAddress = clientSocket.recvfrom(1024)
if response.decode()[:5] == 'ERROR':
    print(response.decode())



    
clientSocket.sendto('OUT'.encode(), (serverIP, serverPort)) 
response, serverAddress = clientSocket.recvfrom(1024)
if response.decode()[:3] == 'BYE':
    logout()
    
if (out_state == True):
    
    clientSocket.close()

'''

