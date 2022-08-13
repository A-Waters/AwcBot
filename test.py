from time import time
from discord.utils import get
import discord
import random
import asyncio
import re
from datetime import datetime, timedelta, time

from secrets import secrets


morning_terms=["wake, morning"]
night_terms=["sleep, night", "tn"]

class MyClient(discord.Client):
    async def on_ready(self):
        self.prefix = '$'
        self.ignore_list = []
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        # only respond to messages with the prefix
        if message.content.startswith(self.prefix):

            if "ignore" in message.content:
                self.ignore_list.append(message.author.id)

            if "attention" in message.content:
                self.ignore_list.remove(message.author.id)

            if "help" in message.content:
                await message.channel.send("``` Here are a list of commands \n * ignore : stop trying to guess my times \n * attention : try to guess my times```")

        else:


            if message.author.id in self.ignore_list:
                return
            
            roles = [y.name.lower() for y in message.author.roles]
            
            time_zone = None

            if "east cost" in roles:
                time_zone = "east"
            
            elif "west cost" in roles:
                time_zone = "west"

            elif "middle cost" in roles:
                time_zone = "central"

            if time_zone == None: 
                return

            
            if (message.author.id == 206117347939975168): # only alow me to activate it 
                times_found = re.findall("((0?1?\d|2[0-3]):([0-5]\d)|24:00)", message.content)

                if times_found == []:
                    times_found = re.findall("([1-9]{1,2}(?=[^0-9])(?=[^0-9,:]))",  message.content)

                if times_found != []:
                    
                    # find indexs of all matching string
                    indexes = []
                    print("TIMES", times_found)
                    for finds in times_found:
                        indexes.append([message.content.find(finds[0], 0, len(message.content)), finds[0]])
                        
                    
                    DayOrNight = None

                    # check of am or pm in sentance
                    for index in indexes:                     

                        if re.search("^\s?am[^a-zA-Z]", message.content[index[0]+len(index[1]):]): 
                            DayOrNight = "day"
                        elif re.search("^\s?pm[^a-zA-Z]", message.content[index[0]+len(index[1]):]):
                            DayOrNight = "night"

                    # check keywords
                    if DayOrNight == None:
                        if any(words in message.content for words in morning_terms):
                            DayOrNight = "day"
                        elif any(words in message.content for words in night_terms):
                            DayOrNight = "night"
                    
                    # get current time time
                    now = datetime.now()
                    current_time = now.time() 

                    ref_time = None

                    message_to_send = ""

                    print(indexes)
                    for index in indexes:

                        try:
                            ref_time = datetime.strptime(index[1], "%I")
                        except:
                            ref_time = datetime.strptime(index[1], "%I:%M")
                        


                        # if current time is past noon and no other times are selected

                        if current_time > time(12,00) and not DayOrNight == "day":
                            ref_time = ref_time + timedelta(hours=12)
                                                
                        
                        if time_zone == "east":
                            west_time = ref_time + timedelta(hours=3)
                            cent_time = ref_time + timedelta(hours=1)
                            east_time = ref_time
                        
                        elif time_zone == "central":
                            west_time = ref_time + timedelta(hours=2)
                            cent_time = ref_time 
                            east_time = ref_time + timedelta(hours=-1)
                        
                        elif time_zone == "west":
                            west_time = ref_time 
                            cent_time = ref_time + timedelta(hours=-2)
                            east_time = ref_time + timedelta(hours=-3)
                        
                        message_to_send += "Ref time: " +ref_time.strftime("%I:%M") + " | West: " + west_time.strftime("%I:%M") + " | Central: " + cent_time.strftime("%I:%M") + " | East: " + east_time.strftime("%I:%M") + " | \n"
                    
                    message_to_send = "```" + message_to_send + "```"

                    await message.channel.send(message_to_send)




client = MyClient()
client.run(secrets['token'])
