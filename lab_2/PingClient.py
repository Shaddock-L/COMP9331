# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 17:03:23 2021

@author: Leyang Li (z5285799) for COMP9331 
"""
from socket import *
import sys
import time
import datetime

serverIP = sys.argv[1]  #read the first pera as the IP address
serverPort = int(sys.argv[2]) #read the second para as the port used by the client
clientSocket = socket(AF_INET, SOCK_DGRAM) #creat a clientSocket 


rtt_list = []
lost_packets = 0

for i in range(15):
    time_start = time.time()
    cr_time = datetime.datetime.now().isoformat(sep =' ')[:-3]
    message = 'Ping' + str(3331+i) + ' ' + cr_time
    clientSocket.settimeout(0.6)
    clientSocket.sendto(message.encode(), (serverIP, serverPort))
    
    try:
        response, serverAddress = clientSocket.recvfrom(1024)
        time_end = time.time()
        rtt_val = (time_end - time_start) * 1000
        rtt_list.append(rtt_val)
        print('ping to ' + serverIP + ', seq = ' +\
              str(i) + ', rtt = ' + str(rtt_val) + ' ms.')
    except timeout:
        lost_packets += 1
        print('ping to ' + serverIP + ', seq = ' + str(i)\
              + ', rtt = time out.')
lost_rate = 100 * (lost_packets / 15)

print('Summary \n\n')
print('Maximum RTT is ' + str(max(rtt_list)) + 'ms.')
print('Minimum RTT is ' + str(min(rtt_list)) + 'ms.')
print('The average RTT is ' + str(sum(rtt_list)/15) + 'ms.')
if lost_packets == 0:
    print('No packet lost.')
else:
    print(str(lost_packets) + 'packets are lost.')
    print('The lost rate is ' + str(lost_rate) + '%.')

