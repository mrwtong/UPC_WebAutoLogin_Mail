#coding=utf-8
import os
import socket
import requests
import urllib
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
#---------------------------Global-Variable--------------------------------------------
url='http://lan.upc.edu.cn/'
refUrl=''
loginUrl='http://lan.upc.edu.cn/eportal/InterFace.do?method=login'
ip=''
senderMail='mrwtong1@163.com'
senderPwd='199559WANG'
senderServer='smtp.163.com'
senderPort=25
mailSubject='E2101工作站IP地址变更的通知'
reqHeader={'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
	'Accept-Encoding':'gzip, deflate',
	'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
	'Connection':'Keep-Alive',
	'Host':'lan.upc.edu.cn',
	'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Mobile Safari/537.36'
}
postHeader={'Accept':'*/*',
	'Accept-Encoding':'gzip, deflate',
	'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
	'Cache-Control':'no-cache',
	'Connection':'Keep-Alive',
	'Content-Length':'339',
	'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
	'Host':'lan.upc.edu.cn',
	'Origin':'http://lan.upc.edu.cn',
	'Pragma':'no-cache',
	'Referer':'',
	'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Mobile Safari/537.36'
}
postData={'userId':'',
	'password':'',
	'service':'',
	'queryString':'',
	'operatorPwd':'',
	'operatorUserId':'',
	'validcode':'',
	'passwordEncrypt':'false'
}
mailMsgTemp="""
<html>
  <head></head>
  <body>
<p>
	<strong><span style="font-size:18px;">{name} 你好：</span></strong> 
</p>
<p>
	<span style="font-size:18px;"><span style="font-size:16px;"><span style="font-size:14px;">工作站</span></span><span style="font-size:14px;"></span><span style="font-size:14px;">连接地址已变更，请使用新地址连接</span><br />
</span> 
</p>
<p>
	<span style="font-size:16px;">-------------------------------------------------</span> 
</p>
<p>
	<span style="font-size:14px;"><strong>一号工作站：</strong></span> 
</p>
<p>
	<span style="font-size:14px;">远程桌面地址：{ip}</span><span style="font-size:14px;">:22100</span> 
</p>
<p>
	<span style="font-size:14px;">文件服务器地址：ftp://<span style="font-size:14px;"><span style="font-size:14px;">{ip}</span>:2021</span></span> 
</p>
<p>
	<span style="font-size:16px;"><br />
</span> 
</p>
<p>
	<span style="font-size:16px;"><strong><span style="font-size:14px;">二号工作站</span></strong><span style="font-size:14px;">：</span></span> 
</p>
<p>
	<span style="font-size:14px;">远程桌面地址：<span style="font-size:14px;"><span style="font-size:14px;">{ip}</span>:22101</span></span> 
</p>
<p>
	<span style="font-size:14px;">文件服务器地址：<span style="font-size:14px;">ftp://</span><span style="font-size:14px;"><span style="font-size:14px;">{ip}</span></span></span><span style="font-size:14px;">:2121</span>
</p>
<p>
	<span style="font-size:16px;"><br />
</span> 
</p>
<p>
	<span style="font-size:14px;"><strong>三号工作站：</strong></span> 
</p>
<p>
	<span style="font-size:16px;"> </span> 
</p>
<p>
	<span style="font-size:14px;">远程桌面地址：<span style="font-size:14px;"><span style="font-size:14px;">{ip}</span>:22102</span></span> 
</p>
<p>
	<span style="font-size:14px;">文件服务器地址：<span style="font-size:14px;">ftp://</span><span style="font-size:14px;"><span style="font-size:14px;">{ip}</span>:2221</span></span> 
</p>
<p>
	<span style="font-size:14px;">---------------------------------------------------------</span> 
</p>
<p>
	<span style="font-size:10px;"><span style="font-size:10px;">^_^</span>Don·t reply me！I am just a stupid Python script working in a router.^_^</span> 
</p>
<p>
	<span style="font-size:10px;"><span style="font-size:10px;">^_^</span>If you want me to work better, please commit your code for&nbsp;<a href="https://github.com/mrwtong/AutoLogin_Mail"target="_blank">me</a>.^_^</span> 
</p>
<p>
	<span style="font-size:16px;"><span style="font-size:10px;">https://github.com/mrwtong/AutoLogin_Mail</span><span style="font-size:10px;"></span><br />
</span> 
</p>
<p>
	<span style="font-size:16px;"><span style="font-size:10px;">http://www.sunpetro.cn/forum.php/</span><span style="font-size:10px;"></span><br />
</span> 
</p>
<p>
	<span style="font-size:16px;"></span> 
</p>
<p>
	<span style="font-size:16px;"></span> 
</p> 
  </body>
</html>
"""#%format(name=userName,ip=ip)
#-----------Recipient Class Define-----------------
class recipient:
    def __init__(self,name,mail):
        self.userName=name
        self.userMail=[mail]
    def Send(self):
        global ip
        global senderMail
        global senderPwd
        global senderServer
        global senderPort
        global mailMsgTemp
        global mailSubject
        mail=MIMEText(mailMsgTemp.format(name=self.userName,ip=ip),'html','utf-8')
        mail['from']=senderMail
        mail['to']=self.userMail[0]
        mail['subject']=Header(mailSubject,'utf-8')
        #--try-send-mail--
        try:
            smtpObj=smtplib.SMTP(senderServer,senderPort)
            #smtpObj.helo()
            #smtpObj.starttls()
            smtpObj.login(senderMail,senderPwd)
            smtpObj.sendmail(senderMail,self.userMail[0],mail.as_string())
            smtpObj.quit()
            return True
        except smtplib.SMTPException as e:
            print "Error：无法发送邮件",e
            return False
#---------Check Login Status-----------------------
def CheckLoginStatus(url):
    global reqHeader
    req=requests.get(url,headers=reqHeader)
    if 'success' in req.url:
        return True
    else:
        global refUrl
        refUrl=req.url
        return False
#-------------Send Login Request----------------------
def SendLoginRequest(userId,password,service):
    global postHeader
    global postData
    global loginUrl
    global refUrl
    global url
#---extract data for http POST---
    postData['userId']=userId
    postData['password']=password
    postData['service']=service
    if refUrl!='':
        postData['queryString']=urllib.quote(refUrl.split('?')[1])
    postHeader['Referer']=refUrl
    postHeader['Content-Length']=str(len(urllib.urlencode(postData)))
#---send post---
    post=requests.post(loginUrl,headers=postHeader,data=postData)
#---check Status---
    if CheckLoginStatus(url):
        return True
    else:
        return False
#---------------Get Host IP-------------
def GetIP():
    try:
        global ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        
    finally:
        s.close()
    if ip=='':
        return False
    else:
        return True
#--------------Get IP Logs-------------------
def GetLogIP():
    with open(os.path.split(os.path.realpath(__file__))[0]+'/ipList','r') as ipfile:
        ipLogs=ipfile.readlines()
        if len(ipLogs)!=0:
            return ipLogs[-1]
        else:
            return '0.0.0.0'
#-----------Append IP--------------------
def AppendIP(ip):
    with open(os.path.split(os.path.realpath(__file__))[0]+'/ipList','a') as ipfile:
         if ipfile.write('\n'+ip):
             return True
         else:
             return False 
#---------------Login---------------------------
def Login():
    with open(os.path.split(os.path.realpath(__file__))[0]+'/accountList','r') as accountfile:
         accountlines=accountfile.readlines()
    if len(accountlines)!=0:
        for i in range(len(accountlines)):
            if SendLoginRequest(accountlines[i].split()[0],accountlines[i].split()[1],accountlines[i].split()[2]):
                return True
            if i==len(accountlines)-1:#i=last accout but cant login
                return False
    else:
        return False
#---------------Send Mail to all users-----------
def SendMailtoAll():
    with open(os.path.split(os.path.realpath(__file__))[0]+'/userList','r') as userfile:
        userlines=userfile.readlines()
        if len(userlines)!=0:
            recipientList=[]
            sendNum=0
            for i in range(len(userlines)):
                recipientList.append(recipient(userlines[i].split()[0],userlines[i].split()[1]))
                if recipientList[i].Send():
                    sendNum=sendNum+1
            if sendNum==len(recipientList):
                return True
            else:
                return False
        else:
            return False

#---------------Script---Start-----------------------------------------------------------
GetIP()
localtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
if CheckLoginStatus(url):
    #Status is Login
    if ip==GetLogIP():
       #---IP is not changed
       #print localtime+' Login,IP Unchanged'
        exit('Log OK, IP OK')
    else:
        AppendIP(ip)
        if SendMailtoAll():
            print localtime+' Login, Send Mail Success'
            exit('Log Ok, Sent Mail')
        else:
            print localtime+' Login, Send Mail Failure'
            exit('Log OK, Sent Fail')
else:
    if Login():
     #ReLogin Ok
        if ip==GetLogIP():
            #IP is not Change
            print localtime+' ReLogin,IP Unchanged'
            exit('Reloged,IP OK')
        else:
            AppendIP(ip)
            if SendMailtoAll():
                print localtime+' ReLogin,Send Mail Success'
                exit('Reloged,Sent Mail')
            else:
                print localtime+' ReLogin,Send Mail Failure'
                exit('Reloged,Sent Fail')
    else:
        print localtime+' Relogin Failure'
        exit('ReLogIn Error')
        
#---------------Test Code----------------------------------------------------------------
'''print(CheckLoginStatus(url))
print(Login())
with open('accountList','r') as accountfile:
    accountlines=accountfile.readlines()
print(len(accountlines))
if len(accountlines)!=0:
    for i in range(len(accountlines)):
        if SendLoginRequest(accountlines[i].split()[0],accountlines[i].split()[1],accountlines[i].split()[2]):
            print(True)
        print(i)
        print accountlines[i].split()[0],accountlines[i].split()[1],accountlines[i].split()[2]
        if i==len(accountlines)-1:#i=last accout but cant login
            print('False1')
else:
   print('False2')
print GetIP()
print(ip)
print mailMsgTemp.format(name='WT',ip=ip)
print SendMailtoAll()'''
