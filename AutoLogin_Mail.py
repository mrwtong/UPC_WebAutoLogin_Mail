# coding=utf-8
# Author: Tong
# Python version: 3.9
# ---------------------------------------------------------------------------
'''
工作流程：
if 网络未登录
    依次尝试使用accountList下的账号登陆网络

if IP地址变更
    保存新的IP地址
    向用所有户发送新IP地址
exit(0)
'''
# ---------------------------------------------------------------------------
import os
import socket
import urllib.request
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header

# ---------------------------Global-Variable--------------------------------------------
## e-mail account

sendMail = True # 若不需要自动发送邮件请修改此项为False
senderMail = 'mrwtong1@163.com' #此处填写邮箱地址
senderPwd = '' #此处填写邮箱密码
senderServer = 'smtp.163.com' #此处填写邮箱服务器号
senderPort = 25
## request data
url = 'http://lan.upc.edu.cn'
refUrl = ''
loginUrl = 'http://lan.upc.edu.cn/eportal/InterFace.do?method=login'
hostIP = ''
reqHeader = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
             'Connection': 'Keep-Alive',
             'Host': 'lan.upc.edu.cn',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
             }
postHeader = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate',
              'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
              'Cache-Control': 'no-cache',
              'Connection': 'Keep-Alive',
              'Content-Length': '339',
              'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
              'Host': 'lan.upc.edu.cn',
              'Origin': 'http://lan.upc.edu.cn',
              'Pragma': 'no-cache',
              'Referer': '',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
              }
postData = {'userId': '',
            'password': '',
            'service': '',
            'queryString': '',
            'operatorPwd': '',
            'operatorUserId': '',
            'validcode': '',
            'passwordEncrypt': 'false'
            }

## email data
mailSubject = '网络IP地址变更的通知'
mailMsgTemp = """{name} 你好：
--------------------------------------------------
工作站连接地址已变更，请使用新地址连接:
    RDP：{ip}:13389
    SSH:{ip}:12222
--------------------------------------------------
This is an automated e-mail by https://github.com/mrwtong/AutoLogin_Mail
"""  # %format(name=userName,ip=ip)


# -----------Recipient Class Define-----------------
class recipient:
    def __init__(self, name, mail):
        self.userName = name
        self.userMail = [mail]

    def Send(self):
        global hostIP
        global senderMail
        global senderPwd
        global senderServer
        global senderPort
        global mailMsgTemp
        global mailSubject
        mail = MIMEText(mailMsgTemp.format(name=self.userName, ip=hostIP), 'plain', 'utf-8')
        mail['from'] = senderMail
        mail['to'] = self.userMail[0]
        mail['subject'] = Header(mailSubject, 'utf-8')
        # --try-send-mail--
        smtpObj = smtplib.SMTP(senderServer, senderPort)
        # smtpObj.helo()
        # smtpObj.starttls()
        smtpObj.login(senderMail, senderPwd)
        smtpObj.sendmail(senderMail, self.userMail[0], mail.as_string())
        smtpObj.quit()
        return


# ---------Check Login Status-----------------------
def CheckLoginStatus(url):
    global reqHeader
    req = urllib.request.Request(url, headers=reqHeader)
    try:
        response = urllib.request.urlopen(req, timeout = 4)
    except Exception:
        localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(localTime + ' :Can not open ' + url)
        exit(0)
    else:
        if 'success' in response.url:
            return True
        else:
            global refUrl
            refUrl = response.url
            return False


# -------------Send Login Request----------------------
def SendLoginRequest(userId, password, service):
    global postHeader
    global postData
    global loginUrl
    global refUrl
    global url
    # ---extract data for http POST---
    postData['userId'] = userId
    postData['password'] = password
    postData['service'] = service
    postData['queryString'] = urllib.parse.quote(refUrl.split('?')[1])
    postHeader['Referer'] = refUrl
    postDataByte = urllib.parse.urlencode(postData).encode()
    postHeader['Content-Length'] = len(postDataByte)
    req = urllib.request.Request(loginUrl, headers=postHeader, data=postDataByte,  method= 'POST')
    # ---send post---
    try:
        response = urllib.request.urlopen(req, timeout=4)
        if response.length is None:
            raise Exception('No response after POST')
    except Exception:
        localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(localTime + ' :Can not post login request to ' + loginUrl)
        exit(0)
    else:
        responseData = response.read().decode('utf-8')
        if 'success' in responseData:
            return True
        elif 'fail' in responseData:
            return False


# ---------------Get Host IP-------------
def GetHostIP():
    try:
        global hostIP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        hostIP = s.getsockname()[0]
    finally:
        s.close()
    if hostIP == '':
        return False
    else:
        return True


# --------------Get IP Logs-------------------
def GetLastIP():
    ipAddr = '0.0.0.0'
    filePath = os.path.split(os.path.realpath(__file__))[0] + '/ipList'
    try:
        with open(filePath, 'r', encoding='utf-8') as ipfile:
            ipLogs = ipfile.readlines()
            for line in reversed(ipLogs):
                if (line != '\n') & (line[0] != '#'):
                    ipAddr = line.replace('\n', '')
                    break
    except Exception:
        localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(localTime + ' :Can not read ipList File in: ' + filePath)
        exit(0)
    else:
        return ipAddr



# -----------Append IP--------------------
def AppendIP(ip):
    filePath = os.path.split(os.path.realpath(__file__))[0] + '/ipList'
    try:
        with open(filePath, 'a', encoding='utf-8') as ipfile:
            ipfile.write('\n' + ip)
    except Exception:
        localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(localTime + ' :Can not write ipList File in: ' + filePath)
        exit(0)
    else:
        return


# ---------------Login---------------------------
def Login():
    filePath = os.path.split(os.path.realpath(__file__))[0] + '/accountList'
    try:
        with open(filePath, 'r', encoding='utf-8') as accountfile:
            accountlines = accountfile.readlines()
        if len(accountlines) != 0:
            for i in range(len(accountlines)):
                if SendLoginRequest(accountlines[i].split()[0], accountlines[i].split()[1], accountlines[i].split()[2]):
                    return
                if i == len(accountlines) - 1:
                    # i = last accout but cant login
                    raise Exception()
        else:
            raise Exception()
    except IOError:
        localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(localTime + ' :Can not read accountList File in: ' + filePath)
        exit(0)
    except Exception:
        localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(localTime + ' :Can not login using account from: ' + filePath)
        exit(0)
    else:
        return


# ---------------Send Mail to all users-----------
def SendMailtoAll():
    userNum = 0
    sendNum = 0
    filePath = os.path.split(os.path.realpath(__file__))[0] + '/userList'
    try:
        with open(filePath, 'r', encoding='utf-8') as userfile:
            userlines = userfile.readlines()
            if len(userlines) != 0:
                for line in userlines:
                    if (line != '\n') & (line[0] != '#'):
                        userNum = userNum + 1
                        receiver = recipient(line.split()[0], line.split()[1])
                        try:
                            receiver.Send()
                        except Exception:
                            pass
                        else:
                            sendNum = sendNum + 1
    except IOError:
        localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(localTime + ' :Can not read userList File in: ' + filePath)
        exit(0)
    else:
        return sendNum, userNum

# ---------------Script---Start-----------------------------------------------------------
if __name__ == '__main__':
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if CheckLoginStatus(url) is False:
        Login()
        print(localtime + ' :Relogin')

    GetHostIP()
    if (hostIP != GetLastIP()) & sendMail:
        sendNum, userNum = SendMailtoAll()
        print(localtime + ' :IP changed, send mails to ' + str(sendNum) + '/' +str(userNum) + ' of users')
        AppendIP(hostIP)

    exit(0)
