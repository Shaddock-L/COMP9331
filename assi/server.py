# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 10:59:28 2021
server.py
Assignment for COMP9331
@author: Leyang Li (z5285799)
"""

from socket import *
import threading
import time
import datetime as dt
import sys



def get_key(dic,v):
    for k in dic:
        if dic[k] == v:
            return k


#login_state = False

# creat the valid username and password dic
authentication= {}
login_time = {}
with open('credentials.txt') as f:
    for line in f:
        user, password = line.split()[0], line.split()[1]
        authentication[user] = password
        login_time[user] = ''
        
        
# list to refuse duplicate login
already_login ={}
seqNum = {}
client_udp_server_port={}
seqCount = 0
Messagenumber = 0
thread_num = 0
#block_times = number_of_consecutive_failed_attempts
block_times = 3
wrong_times = 0
block_state = False



def blockT():
    if (block_state == True): 
        threading.Timer(10, blockT).start()

def logIn(username, password, connectionSocket):
    
    #initial state: offline
    global wrong_times
    global blocktime
    global block_times
    global block_state
    global seqCount
    state = False
    '''
    case1: already online(duplicate)
    case2: blocked
    case3: log in successfully  
    '''     
    # the sequence is important!
    if (username in authentication):
        if(wrong_times > block_times):
            connectionSocket.send(f'Login failed! (blocked)\nPlease retry {blocktime}s later'.encode())
            block_state = True
            blockT()
            time.sleep(blocktime)
            block_state = False 
            wrong_times = 0   
        if (password != authentication[username]):
            wrong_times += 1
            connectionSocket.send('Login failed! (wrong password)'.encode())
            connectionSocket.send(f'wrongtimes: {wrong_times}'.encode())
            
        elif (username in already_login):
            connectionSocket.send('Login failed! (already logged in)'.encode())
            
        
            
        elif (password == authentication[username] and wrong_times <= block_times):
            
            connectionSocket.send('Login successfully!'.encode())
            #recv the udp port
            cli_port = connectionSocket.recv(1024).decode()
            client_udp_server_port[username] = cli_port 
            #record the login time
            login_time[username] = dt.datetime.now()
            #update the state
            state = True
            seqCount += 1
            #Sequence number
            already_login[username] = seqCount
            print(already_login)
            #reset the block times
            wrong_times = 0           
    else:
        wrong_times += 1
        connectionSocket.send('Login failed! (user does not exist)'.encode())
        if(wrong_times > block_times):
            connectionSocket.send(f'Login failed! (blocked)\nPlease retry {blocktime}s later'.encode())
            block_state = True
            blockT()
            time.sleep(blocktime)
            block_state = False 
            wrong_times = 0
        #connectionSocket.send(f'wrongtimes: {wrong_times}\n'.encode())
    
    return state

def logOut(username):
    global already_login
    #rewrite the active login file
    # change the log file name later
    with open (r'.\userlog.txt', 'r') as f:
        a = f.readlines()
        f.close()
    # ensure that the current num is greater than all sequence numbers
    num = len(a) + 1
    for i in range(len(a)):
        #format: #1; 21 Apr 2021 15:00:38; Hans; 127.0.0.1; 6666
        if (a[i] != '\n'):
            s_line = a[i].split('; ')
            sq_num = int(s_line[0][1:])
            if sq_num > num:
                content = f'#{i}; {s_line[1]}; {s_line[2]}; {s_line[3]}; {s_line[4]}'
                a[i] = content
            if (s_line[-3] == username):
                #update num
                num = sq_num
                a[i] = '\n'
    # change the log file name later          
    with open(r'.\userlog.txt','w') as f:
        for line in a:
            if line != '\n':
                f.write(line)
        f.close()
    # reset the already_login dic
    already_login.pop(username)
                
                
    

'''MSG part'''

#Messagenumber; timestamp; username; message; edited
def MSGserver (whoSent, content):
    global Messagenumber
    global connectionSocket
    check_empty = content.split()
    if (content and check_empty):
        Messagenumber += 1

        edt_state =  'no'
        ############modify the file name later
            
        msg_time = time.mktime(dt.datetime.now().timetuple())
        std_time =  dt.datetime.fromtimestamp(msg_time).strftime('%d %b %Y %H:%M:%S')
        with open (r'.\messagelog.txt', 'a+') as f:
            f.write(f'#{Messagenumber}; {std_time}; {whoSent}; {content}; {edt_state}\n')
            f.close()
        print(f'#{Messagenumber}; {std_time}; {whoSent}; {content}; {edt_state}')
        connectionSocket.send('success post'.encode())
    # if the client forget to enter the content
    else:
        connectionSocket.send('ERROR! The content after MSG cannot be null'.encode())
        print('content is null')

def DLT(msg_num, day, month, year, tim, uname):
    # change the log file name later
    #print(msg_num, day, month, year, tim, uname)
    dlt_rst = -1
    with open(r'.\messagelog.txt','r') as f:
        a = f.readlines()
        f.close()
    num = len(a) + 1  
    #with open(r'.\contenttest.txt','w') as f:
    for i in range(len(a)):
        if (a[i] != '\n'):
            s_line = a[i].split('; ')
            #print(s_line)
            h = s_line[0]
            if int(h[1:]) > num:
                content = f'#{i}; {s_line[1]}; {s_line[2]}; {s_line[3]}; {s_line[4]}'
                a[i] = content
            if (h == msg_num):
                #print('match')
                date = s_line[1].split()
                #print(date)
                #print(uname)
                if (date[0] == day and date[1] == month and date[2] == year and uname == s_line[2]):
                    #print('MMMMMatch')
                    num = int(h[1:])
                    a[i] = '\n'
                    dlt_rst = int(h[1:])
                    
    with open(r'.\messagelog.txt','w') as f:
        for line in a:
            if line != '\n':
                f.write(line)
        f.close()        
    return dlt_rst



def EDT(seq_n, day, month, year, tim, new_content, uname):
    edt_rst = -1
    with open(r'.\messagelog.txt','r') as f:
        a = f.readlines()
        f.close() 
    #with open(r'.\contenttest.txt','w') as f:
    for i in range(len(a)):
        if (a[i] != '\n'):
            s_line = a[i].split('; ')
            #print(s_line)
            h = s_line[0]
            if (h == seq_n):
                #print('match')
                date = s_line[1].split()
                #print(date)
                #print(uname)
                if (date[0] == day and date[1] == month and date[2] == year and uname == s_line[2]):
                    #print('MMMMMatch') 
                    edt_time = time.mktime(dt.datetime.now().timetuple())
                    std_edt_time =  dt.datetime.fromtimestamp(edt_time).strftime('%d %b %Y %H:%M:%S')
                    a[i] = f'{seq_n}; {std_edt_time}; {uname}; {new_content}; yes\n'
                    edt_rst = 1          
    with open(r'.\messagelog.txt','w') as f:
        for line in a:
            if line != '\n':
                f.write(line)
        f.close()        
    
    
    return edt_rst

def RDM(time_Stamp):
    rdm_rst= []
    msg_num = 0
    cp_time = time.mktime(time.strptime(time_Stamp,'%d %b %Y %H:%M:%S'))
    # #1; Yoda: “Hello” posted at 23 Feb 2021 15:00:01.
    # ['#1', '13 Apr 2021 17:07:25', 'Hans', 'hELLO WORD', 'no\n']
    with open(r'.\messagelog.txt','r') as f:
        for line in f:
            s_line = line.split('; ')
            msg_time = time.mktime(time.strptime(s_line[1],'%d %b %Y %H:%M:%S'))
            if msg_time > cp_time:
                rdm_rst.append(f'{s_line[0]}; {s_line[2]}: "{s_line[3]}" post at {s_line[1]}.\n')
                msg_num += 1
        f.close()
    return msg_num, rdm_rst

def ATU (username):
    #change the file name later
    atu_rst = []
    with open (r'.\userlog.txt','r') as f:
        a = f.readlines()
        f.close()
    #format: #2; 21 Apr 2021 15:01:18; yoda; 127.0.0.1; 6666
    for line in a:
        s_line = line.split('; ')
        if (s_line[2] == username):
            a.remove(line)
    #case1: other users
    if (a):
        for data in a:
            s_data = data.split('; ')
            atu_rst.append(f'{s_data[2]}, {s_data[3]}, {s_data[4][:-1]}, active since {s_data[1]}')
    #no other users
    else:
        atu_rst.append('no other active user\n')
    
    return atu_rst
        
        






# multiple threads 
def recv_handler():   
    global connectionSocket
    global already_login
    global client_udp_server_port
    global thread_num
    #global login_state
    login_state = False
    thread_num += 1
    print(f'Thread {thread_num} is ready to serving!')
    
    while 1:
        
        if (not login_state):
            connectionSocket.send('Username: '.encode())
            client_name = connectionSocket.recv(1024)
            username = client_name.decode()
            connectionSocket.send('Password: '.encode())
            clt_pass = connectionSocket.recv(1024)
            password = clt_pass.decode()
            login_state = logIn(username,password,connectionSocket)
        
            if login_state:
                client_address = connectionSocket.recv(1024).decode()
                ttuple = time.mktime(login_time[username].timetuple())
                std_time =  dt.datetime.fromtimestamp(ttuple).strftime('%d %b %Y %H:%M:%S')
                info_to_record = f'#{already_login[username]}; {std_time}; {username}; {client_address}; {client_udp_server_port[username]}'
                ########-------------
                ####### change file name for test!!! remember to modify later
                with open (r'.\userlog.txt','a') as f:
                    f.write(info_to_record + '\n')
                    f.close()
                print(info_to_record)
        else:
            connectionSocket.send('Enter one of the commands(MSG, DLT, EDT, RDM, ATU, OUT, UPD):'.encode())
            cmdAsk = connectionSocket.recv(1024).decode()
            print(cmdAsk)
                
            # RECEIVE MSG FORMAT: MSG CONTENT
            if (cmdAsk[:3] == 'MSG'):
                # we should now who want to send the MSG
                # so we need the address
                content = cmdAsk[4:]
                print(f'content is {content}')
                cli_name = connectionSocket.recv(1024).decode()
                MSGserver(cli_name, content)
        
            elif (cmdAsk == 'OUT'):
                cli_name = connectionSocket.recv(1024).decode()
                logOut(cli_name)
                connectionSocket.send(f'BYE! {username}'.encode(),)
                break
            elif (cmdAsk[:3] == 'DLT'):
                #recv username
                #cmd format : DLT #4 23 Feb 2021 16:01:20
                print('ready to delete')
                usname = connectionSocket.recv(1024).decode()
                delete_msg = cmdAsk[4:].split(' ')
                if (delete_msg != ['']):
                    print(delete_msg)
                    dlt_rst = DLT(delete_msg[0], delete_msg[1], delete_msg[2], delete_msg[3], delete_msg[4], usname)
                    if (dlt_rst != -1):# success to delete 
                        dlt_time = time.mktime(dt.datetime.now().timetuple())
                        std_dlt_time =  dt.datetime.fromtimestamp(dlt_time).strftime('%d %b %Y %H:%M:%S')
                        connectionSocket.send(f'Message #{dlt_rst} deleted at {std_dlt_time}.\n'.encode())
                    else:# fail to delete
                        connectionSocket.send(f'Opps, you cannot delete that message, please check your command and try again.'.encode())
                else:# fail to delete
                    connectionSocket.send(f'ERROR! The content after DLT cannot be null.'.encode())
            elif (cmdAsk[:3] == 'EDT'):
                print('ready to edit')
                usname = connectionSocket.recv(1024).decode()
                edt_msg = cmdAsk[4:].split(' ')
                if (edt_msg != ['']):
                    sq_num = edt_msg[0]
                    edt_d = edt_msg[1]
                    edt_m = edt_msg[2]
                    edt_y = edt_msg[3]
                    edt_t = edt_msg[4]
                    new_content = ' '.join(edt_msg[5:])
                    edt_rst = EDT(sq_num,edt_d, edt_m, edt_y, edt_t, new_content, usname)
                    if (edt_rst != -1):# success to delete 
                        edt_time = time.mktime(dt.datetime.now().timetuple())
                        std_edt_time =  dt.datetime.fromtimestamp(edt_time).strftime('%d %b %Y %H:%M:%S')
                        connectionSocket.send(f'Message #{sq_num[1:]} edited at {std_edt_time}.'.encode())
                    else:#fail to edit
                        connectionSocket.send(f'Opps, you cannot edit that message, please check your command and try again.'.encode())
                else:#fail to edit
                    connectionSocket.send(f'ERROR! The content after EDT cannot be null.'.encode())
            
            elif (cmdAsk[:3] == 'RDM'):
                print('ready to READ')
                t_stamp = cmdAsk[4:]
                if t_stamp:
                    msg_count, rdm_rst = RDM(t_stamp)
                    connectionSocket.send(str(msg_count).encode())
                    if (msg_count != 0):
                        for i in range(msg_count):
                            connectionSocket.send(rdm_rst[i].encode())
                else:
                    connectionSocket.send('ERROR! The content after RDM cannot be null.'.encode())
            elif (cmdAsk == 'ATU'):
                cli_name = connectionSocket.recv(1024).decode()
                atu_rst = ATU(cli_name)
                atu_num = len(atu_rst)
                connectionSocket.send(str(atu_num).encode())
                if (atu_rst[0] == 'no other active user\n'):
                    connectionSocket.send(atu_rst[0].encode())
                else:
                    for i in range(atu_num):
                        connectionSocket.send((atu_rst[i]+'\n').encode())                         
            
            #invalid command
            else:
                connectionSocket.send('Error! Invalid command!'.encode())
                print('An invalid command')
                
                
                
          





serverPort = int(sys.argv[1])
number_of_consecutive_failed_attempts = int(sys.argv[2])

'''
-----------------------------------------------------------------------------------
main
-----------------------------------------------------------------------------------
'''

#serverPort = 11000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('127.0.0.1', serverPort))
serverSocket.listen(5) #it specifies the number of unaccepted connections that the system will allow before refusing new connections.

while True:     # 一个死循环，不断的接受客户端发来的连接请求
    connectionSocket, address = serverSocket.accept()  # 等待连接，此处自动阻塞
    # 每当有新的连接过来，自动创建一个新的线程，
    # 并将连接对象和访问者的ip信息作为参数传递给线程的执行函数
    t = threading.Thread(target=recv_handler)
    t.start()




























