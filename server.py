#!/usr/bin/python
import socket
import sys
import thread

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#menerima koneksi dari semua interface
server_address=('',10050)
client_list=list()
auth_list={}
logged={}
group_list={}
group_auth={}

def send_to_all_klien(message):
    for koneksi in client_list:
        try:
            koneksi.sendall(message)
        except:
            koneksi.close()
            client_list.remove(koneksi)

def send_message(koneksi,message):
    try:
        koneksi.sendall(message)
    except:
        print("Send error")
            
def load_user():
    f=open("data.dat","r")
    
    for line in f:
        try:
            line=line.splitlines()
            #print line[0]
            tmp=line[0].strip().split(":")
            #print tmp
            auth_list[tmp[0]]=tmp[1]
        except:
            pass

def register(koneksi,arg):
    f=open("data.dat","a")
    str_user=arg[1]
    str_pass=arg[2]
    
    if auth_list.get(str_user,0)==0:
        str_auth=str_user+":"+str_pass
        f.write(str_auth)
        f.close
        auth_list[str_user]=str_pass
        send_message(koneksi,"+REG_SUCCESS")
#        koneksi.sendall("+REG_SUCCESS")
        return
    else:
        send_message(koneksi,"-USR_REGISTERED")
#        koneksi.sendall("-USR_REGISTERED")
        f.close()

def login(koneksi,arg):
    if len(arg)<3:
        send_message(koneksi,"-SYNTAX_ERROR")
        return 0
    str_user=arg[1]
    str_pass=arg[2].strip()
    
    if logged.get(str_user,0)!=0:
        send_message(koneksi,"+ALREADY_LOGGED_IN")
#        koneksi.sendall("+ALREADY_LOGGED_IN");
        return 0
        
    pass_check=auth_list.get(str_user,0)
    
    if pass_check!=0:
        if str_pass==pass_check:
            send_message(koneksi,"+LOGIN_SUCCESS")
            #koneksi.sendall("+LOGIN_SUCCESS")
            logged[str_user]=koneksi
            return str_user
        else:
            send_message(koneksi,"-WRONG_PASS")
#            koneksi.sendall("-WRONG_PASS")
            return 0
    else:
        send_message(koneksi,"-USER_NOT_FOUND")
#        koneksi.sendall("-USER_NOT_FOUND")
        return 0

def check_logged(userid):
    if logged.get(userid,0)==0:
        return 0
    else:
        return 1

def check_is_me_logged(koneksi,userid):
    if logged.get(userid,0)==0:
        send_message(koneksi,"-YOU_NOT_LOGGED_IN")
#        koneksi.sendall("-YOU_NOT_LOGGED_IN")
        return 0
    else:
        return 1

def create_group(koneksi,arg,userid):
    if check_is_me_logged(koneksi,userid)==0:
        return
        
    group_name=arg[1]
    password=arg[2]
    
    if group_auth.get(group_name,0)!=0:
        send_message(koneksi,"-GROUP_EXISTS")
#        koneksi.sendall("-GROUP_EXISTS")
        return
        
    group_auth[group_name]=password
    group_list[group_name]=list()
    
    tmp=group_list[group_name]=list()
    
    tmp.append(userid)
    send_message(koneksi,"+GROUP_CREATED")
#    koneksi.sendall("+GROUP_CREATED")
    
def list_group(koneksi,arg,userid):
    if check_is_me_logged(koneksi,userid)==0:
        return
     
    groups=group_list.keys()
    group_list.keys()
    for key in groups:
        send_message(koneksi,key+"\n")
#        koneksi.sendall(key+"\n")
    
    send_message(koneksi,"+END_OF_LIST")    
#    koneksi.sendall("+END_OF_LIST")

def join_group(koneksi,arg,userid):
    if check_is_me_logged(koneksi,userid)==0:
        return
    
    group_name=arg[1]
    password=arg[2]
    
    if group_list.get(group_name,0)==0:
        send_message(koneksi,"-GROUP_NOT_FOUND")
#        koneksi.sendall("-GROUP_NOT_FOUND")
        return 0
        
    tmp=group_list[group_name]
    
    if len(tmp) >10:
        send_message(koneksi,"-GROUP_FULL")
#        koneksi.sendall("-GROUP_FULL")
        return 0
        
    if group_auth[group_name]!=password:
        send_message(koneksi,"-WRONG_PASS")
#        koneksi.sendall("-WRONG_PASS")
        return 0
        
    if userid not in tmp:
        tmp.append(userid)
        
    tmp=None
    send_message(koneksi,"+JOINED_SUCCESS")
#    koneksi.sendall("+JOINED_SUCCESS")
        
def list_user(koneksi,arg,userid):
    if check_is_me_logged(koneksi,userid)==0:
        return
        
    group_name=arg[1]
    
    if group_auth.get(group_name,0)==0:
        send_message(koneksi,"-NO_GROUP")
#        koneksi.sendall("-NO_GROUP")
        return
        
    tmp=group_list[group_name]
    
    for val in tmp:
        koneksi.sendall(val+"\n")
        
    send_message(koneksi,"-END_OF_LIST")
#    koneksi.sendall("-END_OF_LIST")
    
def gm(konekasi,arg,userid):
    if check_is_me_logged(koneksi,userid)==0:
        return
        
    group_name=arg[1]
    pesan=arg[2]
    
    if group_list.get(group_name,0)==0:
        send_message(koneksi,"-GROUP_NOT_FOUND")
#        koneksi.sendall("-GROUP_NOT_FOUND")
        return
        
    tmp=group_list[group_name]
    
    if not userid in tmp:
        send_message(koneksi,"-GROUP_NOT_JOINED")
#        koneksi.sendall("-GROUP_NOT_JOINED")
        return 
        
    for user in tmp:
        if user!=userid:
            try:
                kon=logged[user]
                send_message(kon,"GM "+group_name+" "+userid+" "+pesan)
                #kon.sendall("GM "+group_name+" "+userid+" "+pesan)
            except:
                tmp.remove(user)
                print "kirim error"
            
    send_message(koneksi,"+MESSAGE_SENT")
#    koneksi.sendall("+MESSAGE_SENT")
    
def logout(koneksi,arg,userid):
    if check_is_me_logged(koneksi,userid)==0:
        return
        
    del logged[userid]
    
    koneksi.close()
    
def pm(koneksi,arg,userid):
    if check_is_me_logged(koneksi,userid)==0:
        return
    
    sender=userid
    receiver=arg[1]
    message="RPM "+sender+" "+arg[2]
    
    if check_logged(receiver)==0:
        send_message(koneksi,"-USER_NOT_FOUND")
#        koneksi.sendall("-USER_NOT_FOUND")
        return 0
        
    koneksi=logged[receiver]
    send_message(koneksi,message)
        
def koman(koneksi,arg,userid=0):
    arg=arg.rstrip()
    arg=arg.split(" ",2)
    
    print arg
    if arg[0]=="REGISTER":
        if len(arg)<3:
            send_message(koneksi,"-SYNTAX_ERROR")
            return 0
        register(koneksi,arg)
    elif arg[0]=="LOGIN":
        if len(arg)<3:
            send_message(koneksi,"-SYNTAX_ERROR")
            return 0
        login(koneksi,arg)
    elif arg[0]=="PM":
        if len(arg)<3:
            send_message(koneksi,"-SYNTAX_ERROR")
            return 0
        pm(koneksi,arg,userid)
    elif arg[0]=="CREATEGROUP":
        if len(arg)<3:
            send_message(koneksi,"-SYNTAX_ERROR")
            return 0
        create_group(koneksi,arg,userid)
    elif arg[0].rstrip()=="LISTGROUP":
        list_group(koneksi,arg,userid)
    elif arg[0]=="JOIN":
        if len(arg)<3:
            send_message(koneksi,"-SYNTAX_ERROR")
            return 0
        join_group(koneksi,arg,userid)
    elif arg[0]=="LISTUSER":
        if len(arg)<2:
            send_message(koneksi,"-SYNTAX_ERROR")
            return 0
        list_user(koneksi,arg,userid)
    elif arg[0]=="LOGOUT":
        logout(koneksi,arg,userid)
    elif arg[0]=="GM":
        if len(arg)<3:
            send_message(koneksi,"-SYNTAX_ERROR")
            return 0
        gm(koneksi,arg,userid)
    else:
        send_message(koneksi,"-SYNTAX_ERROR")
#        koneksi.sendall("-SYNTAX_ERROR")
        
#------------------------------------------------------------------------------
def klien(koneksi):
    userid=0
    
    while True:
        data = koneksi.recv(1024)
        try:
            if data!="":
                arg=data.split(" ")
                if arg[0]=="LOGIN":
                    userid=login(koneksi,arg)
                    
                    if userid!=0:
                        break
                    else:
                        continue
                        
                koman(koneksi,data)
            else:
                try:
                    koneksi.close()
                except:
                    pass
                if userid!=0:
                    del logged[userid]
                break
        except:
            koneksi.close()
            if userid!=0:
                del logged[userid]
            break
            
    while True:
        try:
            data = koneksi.recv(1024)
            print "lewat"
            if data!="":
                koman(koneksi,data,userid)
            else:
                print "closed"
                logout(koneksi,"",userid)
                break
        except:
            print "closed"
            logout(koneksi,"",userid)
            #koneksi.close()
            break
            
sock.bind(server_address)
sock.listen(1)

load_user()

print auth_list

while True:
    koneksi,addr=sock.accept()
    client_list.append(koneksi)
    thread.start_new_thread(klien,(koneksi,))

koneksi.close()
sock.close()
