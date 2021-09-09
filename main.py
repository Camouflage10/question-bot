import discord
import random
import datetime
import os
import time
from replit import db
from discord.ext import commands, tasks
from webserver import keep_alive

# (random mention) (question)
questions=['Are there any interesting things your name spells with the letters rearranged?','If you were a potato what way would you like to be cooked?','Would you go to space if you knew that you could never come back to earth?','Have you ever been mistaken for someone famous?','What animal would you chose to be?','What is the most embarrassing thing you’ve ever done?','What is the strangest gift you have ever received?','What kind of reality show would you appear in?','Which of Snow White’s seven dwarfs describes you best (Bashful, Doc, Dopey, Grumpy, Happy, Sleepy or Sneezy)?','What song describes your life right now?','How many languages can you speak?','What\'s your middle name?','What is your favorite strange food combinations?','What’s your favorite place?','Where did you grow up?','What\’s your favorite hobby?','If you could be anywhere in the world right now where would you be?','Are you a listener or a talker?','What was your last song on your Spotify?','Are you a back seat driver?','Describe your dream holiday if money was not an issue?','Where do you want to retire?','If you could have any super human power, what would it be?','If you could have any super human power, what would it be?','If you could audition for a talent TV show, what song would you pick and why?','If you could give a piece of advice to your younger self, what would it be?','If you could be a kitchen appliance, what one would you be and why?','If you could be in the Guiness book of world records, what record-breaking feat would you attempt?','If you could have an extra hour of free time everyday, how would you use it?','If you could take 3 things to a desert island what would they be?','If you could have an endless supply of food, what would it be?','If you could speak another language, what would it be?','If you could only listen to once album for the rest of your life, what would it be?']
memberList=[]
recentlyUsed=[10]
interval=3
sendNext=datetime.datetime.now()
# 
channelId=0
activeGulid=""
stopped=False
def rotateUsed(q):
  return
def getRandQuestion():
  q=random.choice(questions)
  #rotateUsed(q)
  return q
def getRandMembers(num):
  mList=[]
  s=''
  for i in range(0,num):
    m=random.choice(memberList)
    while m in mList:
       m=random.choice(memberList)
    mList.append(m)
  for mem in mList:
    s=s+"<@"+str(mem)+">   "
  return s
def getQList():
  s=''
  sList=[]
  for q in questions:
    s=s+q+'\n'
    if len(s)>1500:
      sList.append(s)
      s=''
  if len(s) != 0:
    sList.append(s)
  return sList
def getMList():
  s=""
  sList=[]
  for m in memberList:
    s=s+'<@'+str(m)+'>\n '
    if len(s)>1500:
      sList.append(s)
      s=''
  if len(s) != 0:
    sList.append(s)
  return sList
def saveData():
  db["stopped"]=stopped
  db["questions"]=questions
  db["recentlyUsed"]=recentlyUsed
  db["memberList"]=memberList
  db["interval"]=interval
  db["channelId"]=channelId
  db["sendNext"]=sendNext.strftime('%Y%m%d%H%M%S')
def loadData():
  global questions,recentlyUsed,memberList,interval,channelId,stopped,sendNext
  stopped=db["stopped"]
  questions=db["questions"]
  recentlyUsed=db["recentlyUsed"]
  memberList=db["memberList"]
  interval=db["interval"]
  channelId=db["channelId"]
  sendNext=datetime.datetime.strptime(db["sendNext"],'%Y%m%d%H%M%S')
def help():
  return "!q- used to begin each call\nthis- directs all questions to that channel\nadd (question)-adds question to list in that format\n interval (number)- number is the amount of time between each question in terms of hours\n stop -stops looped quesions\n start - starts looped questions\n show questions- returns the list of question\n show members - returns list of members in mention form\n(mentions)- adds mentioned members after !q command\n delete (mentions)- deletes member from list\n delete (question)- deletes question from list\n next send- sends the time of next question being sent\n"
description = "desc"
intent = discord.Intents.default()
intent.members = True
bot = commands.Bot(command_prefix='!lis', description=description, intent=intent)

def viableChannel():
  global activeGulid
  for guild in bot.guilds:
    for channel in guild.text_channels:
        if channel.id == channelId:
          activeGulid=guild
          return channel
  return False
#startup command
@bot.event
async def on_ready():
    loadData()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    questionLoop.start()
@tasks.loop(hours=.25)
async def questionLoop():
  global sendNext
  if not stopped:
    if datetime.datetime.now()>= sendNext:
      chan=viableChannel()
      print('looped')
      if chan:
        # (random mention) (question)
        #add question to used list
        if len(memberList)>0 and len(questions)>0:
          await chan.send(getRandMembers(3)+': '+getRandQuestion())
          sendNext=datetime.datetime.now()
          sendNext=sendNext.replace(hour=sendNext.hour+interval)
          saveData()
        else:
          await chan.send("either no questions or members")
      else:
        print("no channel has been selected")
    else: print("not time yet")
  else:
    print('stopped by loop')
    questionLoop.stop()
@bot.event
async def on_message(message):
  global channelId
  mess=message.content.split()
  if '!q' in mess:
    if 'this' in mess:
      print(str(message.channel.id))
      channelId=message.channel.id
      await message.channel.send('this channel has been selected')
    elif 'help' in mess:
      await message.channel.send(help())
    elif 'add' in mess:
      q=" ".join(mess[mess.index('add')+1:])
      print(q)
      if q not in questions:
        questions.append(q)
        await message.channel.send(q+" was added to questions")
    elif 'interval' in mess:
      global interval,sendNext
      num=mess[mess.index('interval')+1]
      sendNext=sendNext.replace(hour=sendNext.hour-interval)
      interval=int(num)
      sendNext=sendNext.replace(hour=sendNext.hour+interval)
      print("interval is now"+str(interval))
      await message.channel.send("interval has been changed to "+ str(interval))
    elif 'start' in mess:
      global stopped
      stopped=False
      sendNext=datetime.datetime.now()
      questionLoop.restart()
      print('start')
      await message.channel.send("start sending questions")
    elif 'stop' in mess:
      stopped=True
      questionLoop.stop()
      print("stopped")
      await message.channel.send("stopped sending questions")
    elif 'show' in mess:
      if 'questions' in mess:
        qList=getQList()
        for q in qList:
          await message.channel.send(str(q))
      if 'members' in mess:
        mList=getMList()
        for m in mList:
          await message.channel.send(str(m))
    elif 'delete' in mess:
      if len(message.mentions):
          for mem in message.mentions:
            if mem.id in memberList:
              memberList.remove(mem.id)
            else:
              await message.channel.send(mem.mention+" was not in the list")
      else:
        q=" ".join(mess[mess.index('delete')+1:])
        if q in questions:
          questions.remove(q)
          await message.channel.send(q+" has been removed")
        else:
          await message.channel.send(q+" was not in the list")
    elif len(message.mentions)>0:
      for mem in message.mentions:
        if mem.id not in memberList:
          memberList.append(mem.id)
          await message.channel.send(mem.mention+" has been added")
    elif 'next' and 'send' in mess:
      await message.channel.send("Next time to send: "+str(sendNext))
      await message.channel.send("Now (for server time diff reference): "+str(datetime.datetime.now()))
    saveData()
keep_alive()

bot.run(os.getenv('Token'))