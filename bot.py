import discum
from   colorama import Fore, Back
import datetime
import json
import threading
from enum import Enum
import time
import random
import numpy as np

class State(Enum):
    Disable = -1
    Enable = 0
    Writing = 1
    Reading = 2
    Sleeping = 3

class Bot(object):
    def __init__(self, token, email, password, proxy, captcha, user_agent): 
        self.token      = token
        self.email      = email
        self.password   = password
        #============================
        self.proxy      = proxy
        if str(proxy) == 'nan': self.proxy = ""

        self.captcha    = captcha
        self.user_agent = user_agent
        #============================
        self.connected  = False
        self.valid      = False 
        self.name       = 'Name Unknown'
        self.phone      = 'Phone Unknown'
        self.id         = 'ID Unknown'
        self.guilds     = []
        #============================
        self.allowToSend = True
        self.state = State.Enable # Writing Reading Sleeping  
        #============================

        log = {"console":False, "file":False, "encoding":"utf-8"}
        if(self.token): 
            print("Enter witn Token")
            self.client = discum.Client(token = self.token, log = log) 
            # self.client = discum.Client(token = self.token, proxy = self.proxy, log = log) 
        else: 
            print("Enter witn Password Email")
            self.client = discum.Client(email = self.email, password = self.password, proxy = self.proxy, log = log) 
            self.getToken()
            self.id = self.client._Client__user_id


        self.checkToken()
        self.getGuilds()
        
        # if (self.valid == False): return
        if (self.state == State.Disable): return
        self.client.gateway.command({"function":onInitialize, "params":{"bot": self}})  
        self.client.gateway.run(False) 

    def checkToken(self): 
        self.valid = False
        resp = self.client.checkToken(token=self.token)
        if (resp[0] and resp[1]):
            self.valid = True
            self.state = State.Enable
            print(Back.GREEN + "Valid token: " + self.token + Back.BLACK)
            return True
        
        self.state = State.Disable
        print(Back.RED +  f"Invalid token: {self.token}" + Back.BLACK)  
        return False

    def getToken(self):
        self.token = self.client._Client__user_token
        print(Back.BLUE + f"Get Token: {self.token}" + Back.BLACK)

    def getGuilds(self): 
        resp = self.client.getGuilds()
        self.responseStatus(resp, False)
        for guild in resp.json():
            self.guilds.append(guild["id"])

    def joinGuild(self, link):
        # обрежем ссылку если присутсвует 
        cutBegin = link.find("https://discord.gg/")
        if(cutBegin != -1):
            link = link[cutBegin+19:]

        resp = self.client.joinGuild(link)
        self.responseStatus(resp, False)

        if resp.status_code == 200: 
            self.guilds.append(resp.json()["guild"]["id"])

    def checkGuild(self, guildID):
        if (guildID in self.guilds): 
            print(Back.GREEN + "Присутствует на сервере" + Back.BLACK)
            return True
        else: 
            print(Back.RED + "Отсутствует на сервере" + Back.BLACK)
            return False

    def getChannel(self, channelID):
        resp = self.client.getChannel(channelID)
        self.responseStatus(resp, False)
        return resp.json()

    def sendMessage(self, channelID, message):
        resp = self.client.sendMessage(channelID, message)
        self.responseStatus(resp, False)
        return

    def EnableToSend(self):
        self.state = State.Enable
        self.allowToSend = True

    def Sleep(self, seconds):
        print(f"{self.email} Sleeping TIMER {seconds}")
        self.state = State.Sleeping
        self.t = threading.Timer(seconds, self.EnableToSend).start()

    def ImmitateReading(self, message):
        print("ImmitateReading")
        self.state = State.Reading
        # 700 слов в минуту в среднем/ пусть 10 слов в секунду
        amountWords = len(message.split())
        seconds = int(amountWords / 10)
        seconds += random.randint(5, 10)
        print(f"Читаю сообщение {seconds}сек из {amountWords} слов:{message}")
        time.sleep(seconds) 

    def ImmitateTypingAction(self, message, ChannelID):
        print("typingAction")
        self.state = State.Writing

        size = len(message)
        # print(f"{message} {size} ")

        writingSleepTime  = int(size / 5) # 5 символов в секунду
        writingSleepTime *= random.randint(12, 15)/10 
        print(f"writingSleepTime = {writingSleepTime}")

        row = []
        rowSize = int(writingSleepTime / 5)
        for i in range(rowSize): row.append(5)
        row.append(writingSleepTime - 5 * rowSize)

        print(row)

        for second in row:
            self.client.typingAction(ChannelID)
            sec = 5 + random.randint(1, 3)
            print(f"Writing Sleep {second} sec")
            time.sleep(second) 

    def responseStatus(self, resp, printResponse):
        date = datetime.datetime.today()
        if 200 <= resp.status_code < 300: print(Back.GREEN + date.strftime('%H:%M:%S') +  f" SUCCESS {resp.status_code} by {self.email}" + Back.BLACK)
        else:                             print(Back.RED   + date.strftime('%H:%M:%S') +  f" ERROR {resp.status_code} by {self.email} response:{resp.json()}" + Back.BLACK)
        
        if (printResponse): print(json.dumps(resp.json(), sort_keys=True, indent=4))
        return resp.status_code
# =================================================================
# @bot.gateway.command
def onInitialize(resp, bot):

    if resp.event.ready_supplemental:
        bot.client.gateway.log = {"console":False, "file":False}  # True False

        date = datetime.datetime.today()

        bot.connected = bot.client.gateway.connected

        if (bot.connected):     print(Back.GREEN + f"Gateway Connected: {bot.connected} by {bot.email}" + Back.BLACK)
        if (not bot.connected): print(Back.RED   + f"Gateway Connected: {bot.connected} by {bot.email}" + Back.BLACK)

        if (bot.connected):
            print(Back.BLUE + f"Proxy {bot.client.gateway.proxy_host}:{bot.client.gateway.proxy_port} type={bot.client.gateway.proxy_type} auth={bot.client.gateway.proxy_auth} session_id = {bot.client.gateway.session_id}" + Back.BLACK)

            sessionRead = bot.client.gateway.session.read()

            bot.name    = bot.client.gateway.session.user['username']
            bot.phone   = bot.client.gateway.session.user['phone']
            bot.id      = bot.client.gateway.session.user['id']
            bot.guilds  = bot.client.gateway.session.guildIDs

            print(bot.name)
            print(bot.phone)
            # print(bot.guilds) 
        bot.client.gateway.log = {"console":False, "file":False}
        bot.client.gateway.close() 
