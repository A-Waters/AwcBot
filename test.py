from time import time
from discord.utils import get
import discord
import re
from datetime import datetime, timedelta, time

from secrets import secrets



morning_terms=["wake, morning"]
night_terms=["sleep, night", "tn"]

def get_unix_epochs(Gdatetime):
    return (Gdatetime-datetime(1970,1,1)).total_seconds()+18000.0

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

            if "embed" in message.content:
                names=[str(i) for i in range(10)]
                names = '\n'.join(names);
                embedVar = discord.Embed(title="Time", description="Desc", color=0x00ff00)
                embedVar.add_field(name="Ref", value=names, inline=True)
                embedVar.add_field(name="Local", value="<t:1543392060>", inline=True)
                await message.channel.send(embed=embedVar)

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
                embedVar = discord.Embed(title="Time", description="Desc", color=0x00ff00)
                
                ref_times_list = []
                local_times = []
                


                now = datetime.now()
                current_time = now.time()
                current_date = now.date()

                for i in range(len(found)):
                    time_string = found[i][0] + "-" + found[i][1] +"-"+str(current_date)
        
                    time_string = time_string.replace(" ","")
                    # print(time_string)
                    ref_time = None

                    if (found[i][1]==""):

                        if ':' in time_string:
                            ref_time = datetime.strptime(time_string, "%I:%M--%Y-%m-%d")
                        else:
                            ref_time = datetime.strptime(time_string, "%I--%Y-%m-%d")
                        
                        if current_time > ref_time.time():
                            ref_time = ref_time + timedelta(hours=12)
                        
                    else:
                        if ':' in time_string:
                            ref_time = datetime.strptime(time_string, "%I:%M-%p-%Y-%m-%d")
                        else:
                            ref_time = datetime.strptime(time_string, "%I-%p-%Y-%m-%d")
                    
                    real_time = ref_time
                    
                    # if time_zone == "east":
                    #     real_time = real_time + timedelta(hours=-1)
                    
                    if time_zone == "central":
                        real_time = real_time + timedelta(hours=-1)
                    
                    elif time_zone == "west":
                        real_time = real_time + timedelta(hours=-3)
                    
                    ts = get_unix_epochs(real_time)
                    # print(ts-1660402800)
                    # ref_times_list.append(ref_time.strftime("%I:%M %p"))
                    # local_times.append("<t:"+str(int(ts))+":t>")
                    message_to_send += "***Ref time:*** " + ref_time.strftime("%I:%M %p") + " | ***Local:*** <t:"+str(int(ts))+":t> \n"
                    # message_to_send += "***Ref time:*** " + ref_time.strftime("%I:%M %p") + " | ***Local:*** <t:"+str(int(ts))+":t>" + " | \nPST: " + west_time.strftime("%I:%M %p") + " | CT: " + cent_time.strftime("%I:%M %p") + " | EST: " + east_time.strftime("%I:%M %p") + " | \n"
                


                message_to_send = ">>> " + message_to_send
                # ref_times_list = '\n'.join(ref_times_list);
                # local_times = '\n'.join(local_times);
                # embedVar.add_field(name="Ref Time",value=ref_times_list, inline=True)
                # embedVar.add_field(name="Local", value=local_times, inline=True)

                await message.channel.send(message_to_send)


client = MyClient()
client.run(secrets['token'])
