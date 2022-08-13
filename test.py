from time import time
from discord.utils import get
import discord
import re
from datetime import datetime, timedelta, time

from secrets import secrets


morning_terms=["wake, morning"]
night_terms=["sleep, night", "tn"]

class MyClient(discord.Client):
    async def on_ready(self):
        self.prefix = '$'
        self.ignore_list = []
        # print('Logged in as')
        # print(self.user.name)
        # print(self.user.id)
        # print('------')

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

            found = re.findall("((?:0?1?\d|2[0-3]):(?:[0-5]\d)(?: ?)|24:00(?: ?)|(?<!\d)[0-9]{1,2}(?: ?)(?=[apAP]))(?:(?<=[\d ])(am|AM|Am|pm|PM|Pm)\s?)?", message.content)
            
            if found != []:
                
                message_to_send = ""

                for i in range(len(found)):
                    time_string = found[i][0] + "-" + found[i][1]
        
                    time_string = time_string.replace(" ","")
                    
                    ref_time = None

                    if (found[i][1]==""):
                        
                        if ':' in time_string:
                            ref_time = datetime.strptime(time_string, "%I:%M-")
                        else:
                            ref_time = datetime.strptime(time_string, "%I-")
                        
                        now = datetime.now()
                        current_time = now.time() 

                        if current_time > ref_time.time():
                            ref_time = ref_time + timedelta(hours=12)
                    else:
                        if ':' in time_string:
                            ref_time = datetime.strptime(time_string, "%I:%M-%p")
                        else:
                            ref_time = datetime.strptime(time_string, "%I-%p")


                    
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
                    
                    message_to_send += "Ref time: " +ref_time.strftime("%I:%M %p") + " | West: " + west_time.strftime("%I:%M %p") + " | Central: " + cent_time.strftime("%I:%M %p") + " | East: " + east_time.strftime("%I:%M %p") + " | \n"
                
            message_to_send = "```" + message_to_send + "```"

            await message.channel.send(message_to_send)




client = MyClient()
client.run(secrets['token'])
