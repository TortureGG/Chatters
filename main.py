from bot import Bot
from bot import State
import json
import time
import pandas as pd
from   colorama import Fore, Back



def print_color(text, BackColor, ForeColor):
    print(BackColor + ForeColor + str(text) + Back.BLACK + Fore.WHITE)

def readFile(path):

    result = None
    if (path.find(".txt") != -1): 
            with open(path, encoding='utf-8') as file: result = file.read().splitlines()
            file.close()

    if (path.find(".json") != -1):
            with open(path, encoding='utf-8') as file: result = json.load(file)
            file.close()

    # print(result)
    return result

def Dialog(bot):
    dialog = readFile("dialog.txt")
    ratelimit = bot[0].getChannel(ChannelID)["rate_limit_per_user"]

    for i in range(len(dialog)):
        print(f"\nMessage = {dialog[i]}")
        # определим какой из ботов сейчас будет писать 

        curent = 0
        if  (dialog[i].find("[1]:")  != -1): 
            curent = 1
            actionBot = bot[0]

        elif(dialog[i].find("[2]:") != -1): 
            curent = 2
            actionBot = bot[1]
        
        message = dialog[i][4:]
        #reading===============================================
        prev = 0
        if(i != 0 ): 
            if  (dialog[i-1].find("[1]:") != -1): prev = 1
            elif(dialog[i-1].find("[2]:") != -1): prev = 2

            if(curent != prev):
                actionBot.ImmitateReading(dialog[i-1])
        #if sleeping============================================
        print(f"{actionBot.email} : {actionBot.state}")
        while (actionBot.state == State.Sleeping):
            time.sleep(1)
            print(f"{actionBot.email} : {actionBot.state}")
        #writing================================================
        actionBot.ImmitateTypingAction(message, ChannelID)
        actionBot.sendMessage(ChannelID, message)
        actionBot.Sleep(ratelimit)

def JoinOnServer(bots):
    for bot in bots:
        bot.joinGuild(InviteLink)

def deleteInvalidBots(bots):
    botToDelete = []
    for bot in bots:
        if bot.state == State.Disable: 
            print_color(f"Бот исключен: {bot.email} {bot.token}", Back.BLUE, Fore.WHITE)
            botToDelete.append(bot)

    for bot in botToDelete:     
        bots.remove(bot)

    print_color(f"\nВсего ботов добавлено: {len(bots)}", Back.BLUE, Fore.WHITE)


def Main():
    global ChannelID, ServerID, InviteLink

    botsExcel = pd.read_excel('bots.xlsx', sheet_name='Лист1')
    # print(botsExcel)

    config = readFile("config.json")
    ChannelID   = config["Channel"]
    ServerID    = config["Server"]
    InviteLink  = config["invite_link"]

    if ChannelID == "": return
    if ServerID == "": return
    # if InviteLink == "": return

    bots = []
    for i in range(len(botsExcel)):
        bots.append(Bot(email       = botsExcel['Email'][i], 
                        password    = botsExcel['Password'][i], 
                        token       = botsExcel['Token'][i], 
                        proxy       = botsExcel['Proxy'][i], 
                        captcha     = '', 
                        user_agent  = botsExcel['user_agent'][i]))
    
    deleteInvalidBots(bots)
    JoinOnServer(bots)
    # Dialog(bots)

#===============================================================================
Main()
#===============================================================================