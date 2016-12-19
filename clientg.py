#!/usr/bin/env python

import npyscreen, curses
import thread
import socket
import sys
from thread import *
import os  
import time  

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_address = ('10.151.36.250', 10040)

sock.connect(server_address)
nama=''
err_list={}

err_list['501']="berhasil gabung group" 
err_list['502']="gagal karena group tidak ada" 
err_list['503']="gagal join karena sudah join grup yg dituju"
err_list['401']="grup berhasil dibuat" 
err_list['402']="gagal karena nama group sudah ada"
err_list['403']="gagal karena kesalahan format parameter"
err_list['301']="pesan personal terkirim" 
err_list['302']="gagal karena username penerima tidak ada" 
err_list['303']="gagal karena username sedang tidak online" 
err_list['304']="gagal karena message kosong"
err_list['001']="command salah"
err_list['002']="anda belum login"
err_list['003']="anda sudah login"
err_list['004']="menampilkan list grup yang ada"
err_list['101']="registrasi berhasil"
err_list['102']="registrasi gagal username sudah ada"
err_list['103']="registrasi gagal kesalahan format"
err_list['201']="berhasil masuk"
err_list['202']="login gagal username/password salah"
err_list['301']="pesan personal terkirim" 
err_list['302']="gagal karena username penerima tidak ada" 
err_list['303']="gagal karena username sedang tidak online" 
err_list['304']="gagal karena message kosong"
err_list['401']="grup berhasil dibuat" 
err_list['402']="gagal karena nama group sudah ada" 
err_list['403']="gagal karena kesalahan format parameter"
err_list['501']="berhasil gabung group" 
err_list['502']="gagal karena group tidak ada" 
err_list['503']="gagal join karena sudah join grup yg dituju"
err_list['601']="berhasil keluar group"
err_list['602']="gagal karena anda belum masuk group"
err_list['603']="gagal karena group tidak ada"
err_list['701']="SENDG OK pesan terkirim"
err_list['702']="SENDG FAILED grup tidak ada"
err_list['703']="SENDG FAILED message kosong"
err_list['704']="SENDG FAILED user belum tergabung"
err_list['801']="pesan public/broadcast terkirim"
err_list['803']="gagal karena message kosong"
err_list['005']="EndList"

class MyTestApp(npyscreen.NPSAppManaged):
    def onStart(self):
        #self.keypress_timeout_default = 1
        self.a=self.addForm("MAIN", mainform)
        self.res=""
        
                
    def while_waiting(self):
        pass
#        print "lala"
        
               
        
class mainform(npyscreen.ActionForm):
    def create(self):
        self.keypress_timeout_default = 1
        #super(mainform, self).create()
        self.resp = self.add(npyscreen.MultiLineEdit, max_height=7)
        self.usrid=self.add(npyscreen.TitleText, name = "UserId:", value="")
        self.grpid=self.add(npyscreen.TitleText, name = "GroupId:", value="")
        self.mes=self.add(npyscreen.TitleText, name = "Message:", value="")
        self.sendbutton = self.add(npyscreen.ButtonPress, name='Send',rely=13)
        self.sendgbutton = self.add(npyscreen.ButtonPress, name='Send To Group',rely=13,relx=9)
        self.regbutton = self.add(npyscreen.ButtonPress, name='Register',rely=16)
        self.logbutton = self.add(npyscreen.ButtonPress, name='Login',rely=16,relx=13)
        self.lsuserbutton = self.add(npyscreen.ButtonPress, name='List User',rely=16,relx=20)
        self.logoutbutton = self.add(npyscreen.ButtonPress, name='Logout',rely=16,relx=31)
        self.cgroupbutton = self.add(npyscreen.ButtonPress, name='Create Group',rely=18)
        self.jgroupbutton = self.add(npyscreen.ButtonPress, name='Join Group',rely=18,relx=17)
        self.lgroupbutton = self.add(npyscreen.ButtonPress, name='Leave Group',rely=18,relx=30)
        self.lsgroupbutton = self.add(npyscreen.ButtonPress, name='List Group',rely=18,relx=44)
        
        self.regbutton.whenPressed = self.register
        self.logbutton.whenPressed = self.login
        self.lsuserbutton.whenPressed = self.listuser
        self.sendbutton.whenPressed = self.pm
        self.cgroupbutton.whenPressed = self.creategroup
        self.jgroupbutton.whenPressed = self.joingroup
        self.lgroupbutton.whenPressed = self.leavegroup
        self.lsgroupbutton.whenPressed = self.listgroup
        self.sendgbutton.whenPressed = self.sendgroup
        self.logoutbutton.whenPressed = self.logout
        thread.start_new_thread(self.receive,())
    
    def receive(self):
        while True:
            data = sock.recv(1024)
            if err_list.get(data.strip(),0)!=0:
                time.sleep(1)
                npyscreen.notify_wait(err_list[data.strip()], title='Warning')
                time.sleep(0.5)
#            print ps_error
            else:
                self.resp.value=self.resp.value+data.decode()
                self.resp.display()
                
    def frmreg(*args):
        F = npyscreen.Form(name='Register')
        usr=F.add(npyscreen.TitleText, name="Username: ")
        pas=F.add(npyscreen.TitleText, name="Password: ")
        F.edit() 
        return (usr.value,pas.value)
        
    def frmcgroup(*args):
        F = npyscreen.Form(name='Create Group')
        groupname=F.add(npyscreen.TitleText, name="Group Name: ")
        F.edit() 
        return groupname.value
        
    def frmjgroup(*args):
        F = npyscreen.Form(name='Join Group')
        groupname=F.add(npyscreen.TitleText, name="Group Name: ")
        F.edit() 
        return groupname.value
    
    def frmlgroup(*args):
        F = npyscreen.Form(name='Leave Group')
        groupname=F.add(npyscreen.TitleText, name="Group Name: ")
        F.edit() 
        return groupname.value
        
    def frmlog(*args):
        F = npyscreen.Form(name='Login')
        usr=F.add(npyscreen.TitleText, name="Username: ")
        pas=F.add(npyscreen.TitleText, name="Password: ")
        F.edit() 
        return (usr.value,pas.value)       
        
    def pm(self):
        if (self.mes.value!=''):
            msg=""
            if(self.usrid.value!=''):
                msg="SENDP " + self.usrid.value+ " " + self.mes.value
            else:
                msg="SEND " + "PUBLIC " + self.mes.value
                
            sock.sendall(msg)
            
    def sendgroup(self):
        if (self.mes.value!='' and self.grpid.value!=''):
            msg="SENDG " + self.grpid.value + " " + self.mes.value     
            sock.sendall(msg)
    
    def logout(self):
        sock.sendall("LOGOUT")
        
    def listuser(self):
        sock.sendall("LISTUS")
        
    def listgroup(self):
        sock.sendall("LISTGR")
        
    def creategroup(self):
        groupname=npyscreen.wrapper_basic(self.frmcgroup)
        sock.sendall("CREATE "+groupname)
        
    def joingroup(self):
        groupname=npyscreen.wrapper_basic(self.frmjgroup)
        sock.sendall("JOIN "+groupname)
        
    def leavegroup(self):
        groupname=npyscreen.wrapper_basic(self.frmlgroup)
        sock.sendall("LEAVE "+groupname)
        
    def login(self):
        (usr,pas)=npyscreen.wrapper_basic(self.frmreg)
        msg="LOGIN "+usr+" "+pas
        sock.sendall(msg)
        
    def register(self):
        (a,b)=npyscreen.wrapper_basic(self.frmreg)
        msg="REGIST "+a+" "+b
        sock.sendall(msg)
        
        
    def while_waiting(self):
	    pass
	    
def display_mainform():
    mf=MyTestApp()
    print mf
    mf.run()
    return 0
        
def main():
    display_mainform()
    
    
if __name__ == '__main__':
    main()
    
