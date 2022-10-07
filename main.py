from time import time, timezone
from discord.utils import get
import discord
import re
from datetime import timedelta, time, tzinfo
import datetime as dt
import openai
import subprocess


from local_secrets import local_secrets


openai.api_key = local_secrets['openai']
start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

morning_terms=["wake, morning"]
night_terms=["sleep, night", "tn"]

def get_unix_epochs(date_time):
    return (date_time-dt.datetime(1970,1,1, tzinfo=dt.timezone.utc)).total_seconds()

class MyClient(discord.Client):
    async def on_ready(self):
        self.prefix = '$'
        self.ignore_list = []
        self.useable = []
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

            elif "attention" in message.content:
                self.ignore_list.remove(message.author.id)

            elif "help" in message.content:
                await message.channel.send("``` Here are a list of commands \n * ignore : stop trying to guess my times \n * attention : try to guess my times \n * list roles : list all the roles a user can add and remove to themselves \n * add role : add a role to them selves '$add role minecraft' \n * remove role : remove a role from themselves '$remove role minecraft' \n * use me : use smart AI to talk to you \n * please stop : stop using smart AI to talk to you ```")

            elif "list roles" in message.content:           
                message_to_send = "```Here are a list of roles I can add and Remove:\n"
                i = 1 
                for role in [role.name for role in self.listRoles(message)]:
                    if i % 4 != 0:
                        message_to_send += role + " | "
                    else:
                        message_to_send += role + "\n"
                    
                    i += 1
                    
                message_to_send += "```"
                await message.channel.send(message_to_send)

            elif "add role" in message.content:
                role_to_add_name = message.content.split("role")[1].strip()
                role_names = [role.name for role in self.listRoles(message)]
                role_to_add = None
                for role in self.listRoles(message):
                        if role.name == role_to_add_name:
                            role_to_add = role
                            break

                if role_to_add_name in role_names and role_to_add not in message.author.roles:
                    await message.author.add_roles(role_to_add)
                    await message.add_reaction('✅')
                    
                else:
                    await message.add_reaction('❌')


            elif "remove role" in message.content:
                role_to_remove_name = message.content.split("role")[1].strip()
                role_names = [role.name for role in self.listRoles(message)]
                role_to_remove = None
                for role in self.listRoles(message):
                        if role.name == role_to_remove_name:
                            role_to_remove = role
                            break

                if role_to_remove_name in role_names and role_to_remove in message.author.roles:
                    await message.author.remove_roles(role_to_remove)
                    await message.add_reaction('✅')
                    
                else:
                    await message.add_reaction('❌')

            elif "use me" in message.content:
                self.useable.append(message.author.id)
                await message.add_reaction('✅')

            elif "please stop" in message.content and message.author.id in self.useable:
                self.useable.append(message.author.id)
                await message.add_reaction('✅')

            elif "update" in message.content:
                rc = subprocess.call("/home/alex/Documents/DiscordTimeBox/autopull.sh")

            ''' if "embed" in message.content:
                 names=[str(i) for i in range(10)]
                names = '\n'.join(names)
                embedVar = discord.Embed(title="Commands", description="A list of commands I use", color=0x00ff00)
                embedVar.add_field(name="Command", value=names, inline=True)
                embedVar.add_field(name="Description", value="", inline=True)
                await message.channel.send(embed=embedVar)'''



        else:
            if message.author.id in self.ignore_list:
                return
            
            if message.content.startswith("http"):
                return 

            if message.author.id in self.useable:
                prompt_to_send = "Human: Hello\nAi: Hello"+message.content + "\nAi:"
                message_to_send = openai.Completion.create(engine="text-ada-001",
                    prompt=prompt_to_send, 
                    temperature=0.9,
                    max_tokens=25,
                    presence_penalty=0.6,
                    frequency_penalty=0.1,
                    stop=["Human:", "AI:"]
                ).choices[0].text

            else:

                roles = [y.name.lower() for y in message.author.roles]
                
                time_zone = None

                if "east coast" in roles:
                    time_zone = "EST"
                    offset = "-0400"
                
                elif "middle coast" in roles:
                    time_zone = "CT"
                    offset = "-0500"

                elif "west coast" in roles:
                    time_zone = "PST"
                    offset = "-0700"



                if time_zone == None: 
                    return

                found = re.findall("((?:0?1?\d|2[0-3]):(?:[0-5]\d)(?: ?)|24:00(?: ?)|(?<!\d)[0-9]{1,2}(?: ?)(?=[apAP]))(?:(?<=[\d ])(am|AM|Am|pm|PM|Pm)\s?)?", message.content)
                
                if found != []:
                    
                    message_to_send = ""
                    embedVar = discord.Embed(title="Time", description="Desc", color=0x00ff00)
                    
                    now = dt.datetime.now()
                    current_time = now.time()
                    current_date = now.date()

                    for i in range(len(found)):
                        time_string = found[i][0] + "-" + found[i][1] +"-"+str(current_date)+"-"+offset
            
                        time_string = time_string.replace(" ","")
                        
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
                    
                        message_to_send += "*** "+ time_zone +":***  "+ ref_time.strftime("%I:%M %p") + " | ***Local:*** <t:"+str(int(ts))+":t> \n"
                        
                    message_to_send = ">>> " + message_to_send
                    
            await message.channel.send(message_to_send)
    
    
    def listRoles(self, message):
        return [role for role in message.guild.roles if role.color.value == 16777215] 
         
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(local_secrets['token'])
