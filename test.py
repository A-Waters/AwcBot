from time import time, timezone
from discord.utils import get
import discord
import re
from datetime import timedelta, time, tzinfo
import datetime as dt
import pytz

from secrets import secrets



morning_terms=["wake, morning"]
night_terms=["sleep, night", "tn"]

def get_unix_epochs(date_time):
    return (date_time-dt.datetime(1970,1,1, tzinfo=dt.timezone.utc)).total_seconds()

class MyClient(discord.Client):
    async def on_ready(self):
        self.prefix = '$'
        self.ignore_list = []
        # print(pytz.all_timezones)
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
                time_zone = "EST"
                offset = "-0400"
            
            elif "middle cost" in roles:
                time_zone = "CT"
                offset = "-0500"

            elif "west cost" in roles:
                time_zone = "PST"
                offset = "-0700"



            if time_zone == None: 
                return

            found = re.findall("((?:0?1?\d|2[0-3]):(?:[0-5]\d)(?: ?)|24:00(?: ?)|(?<!\d)[0-9]{1,2}(?: ?)(?=[apAP]))(?:(?<=[\d ])(am|AM|Am|pm|PM|Pm)\s?)?", message.content)
            
            if found != []:
                
                message_to_send = ""
                embedVar = discord.Embed(title="Time", description="Desc", color=0x00ff00)
                
                ref_times_list = []
                local_times = []
                


                now = dt.datetime.now()
                current_time = now.time()
                current_date = now.date()

                for i in range(len(found)):
                    time_string = found[i][0] + "-" + found[i][1] +"-"+str(current_date)+"-"+offset
        
                    time_string = time_string.replace(" ","")
                    # print(time_string)
                    ref_time = None

                    if (found[i][1]==""):

                        if ':' in time_string:
                            ref_time = dt.datetime.strptime(time_string, "%I:%M--%Y-%m-%d-%z")
                        else:
                            ref_time = dt.datetime.strptime(time_string, "%I--%Y-%m-%d-%z")
                        
                        if current_time > ref_time.time():
                            ref_time = ref_time + timedelta(hours=12)
                        
                    else:
                        if ':' in time_string:
                            ref_time = dt.datetime.strptime(time_string, "%I:%M-%p-%Y-%m-%d-%z")
                        else:
                            ref_time = dt.datetime.strptime(time_string, "%I-%p-%Y-%m-%d-%z")
                    
                    loc_time = ref_time
                    ts = get_unix_epochs(loc_time.astimezone())
                    # print(ts-1660402800)
                    # ref_times_list.append(ref_time.strftime("%I:%M %p"))
                    # local_times.append("<t:"+str(int(ts))+":t>")
                    message_to_send += "*** "+ time_zone +":***  "+ ref_time.strftime("%I:%M %p") + " | ***Local:*** <t:"+str(int(ts))+":t> \n"
                    # message_to_send += "***Ref time:*** " + ref_time.strftime("%I:%M %p") + " | ***Local:*** <t:"+str(int(ts))+":t>" + " | \nPST: " + west_time.strftime("%I:%M %p") + " | CT: " + cent_time.strftime("%I:%M %p") + " | EST: " + east_time.strftime("%I:%M %p") + " | \n"
                


                message_to_send = ">>> " + message_to_send
                # ref_times_list = '\n'.join(ref_times_list);
                # local_times = '\n'.join(local_times);
                # embedVar.add_field(name="Ref Time",value=ref_times_list, inline=True)
                # embedVar.add_field(name="Local", value=local_times, inline=True)

                await message.channel.send(message_to_send)


client = MyClient()
client.run(secrets['token'])
