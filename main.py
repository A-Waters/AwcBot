import random
from time import time, timezone
from discord.utils import get
import discord
from discord.ext import commands, tasks
import re
from datetime import timedelta, time, tzinfo
import datetime as dt
import openai
import subprocess
import requests
from time import sleep
import pandas as pd
import datetime


from local_secrets import local_secrets


openai.api_key = local_secrets['openai']
start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

morning_terms=["wake, morning"]
night_terms=["sleep, night", "tn"]


dateparse = lambda x: dt.datetime.strptime(x, '%B %d')





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
        
        
        # birthday stuff
        self.load_birthdays()


    def save_birthdays(self,):
        df = pd.DataFrame.from_dict(self.birthdays, orient="index")
        df.to_csv("./data.csv", header=False, date_format="%B %d")

    def load_birthdays(self,):
        headers = ['UserID', 'Date']
        dtypes = {'UserID': 'str', 'Date': 'str'}
        parse_dates = ['Date']
        self.birthdays = {}
        try:
            self.birthdays = pd.read_csv("./data.csv", 
                    index_col=0,
                    names=headers, 
                    dtype=dtypes, 
                    parse_dates=parse_dates,
                    date_parser=dateparse).squeeze("columns").to_dict()
            self.called_once_a_day.start()
        except FileNotFoundError:
            pass


    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        # only respond to messages with the prefix
        if message.content.startswith(self.prefix):
            
            # tell the bot to ignore you
            if "ignore" in message.content:
                self.ignore_list.append(message.author.id)

            # tell the bot to not ignore you
            elif "attention" in message.content:
                self.ignore_list.remove(message.author.id)

            # elp
            elif "help" in message.content:
                await message.channel.send("``` Here are a list of commands \n * ignore : stop trying to guess my times \n * attention : try to guess my times \n * list roles : list all the roles a user can add and remove to themselves \n * add role : add a role to them selves '$add role minecraft' \n * remove role : remove a role from themselves '$remove role minecraft' \n * use me : use smart AI to talk to you \n * please stop : stop using smart AI to talk to you \n * add birthday : '$add birthday March 31' birthday notification for the server \n * remove birthday : '$remove birthday @user' remove birthday notification for the server \n * list birthdays : see all birthdays saved in DB```")

            # list roles the bot can manage
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
            

            # add a role to a user
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

            # remove a role to a user
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




            # GPT3 bot
            elif "use me" in message.content:
                self.useable.append(message.author.id)
                await message.add_reaction('✅')

            elif "please stop" in message.content and message.author.id in self.useable:
                self.useable.remove(message.author.id)
                await message.add_reaction('✅')


            # update bot to most recent commit
            elif "update" in message.content:
                rc = subprocess.call("/home/alex/Documents/DiscordTimeBox/autopull.sh")



            # add user brithday : add birthday March 31
            elif "add birthday" in message.content:
                date = message.content.split("add birthday")[1]
                
                try:
                    date = datetime.datetime.strptime(date.strip(), "%B %d")
                    
                except :
                    await message.channel.send("Bad date format")
                    return
                
                self.birthdays[str(message.author.id)] = date
                self.save_birthdays()
                await message.add_reaction('✅')


            elif "remove birthday" in message.content:
                user = message.content.split("remove birthday")[1].replace("<@","").replace(">","").strip()
                self.birthdays.pop(str(user))

                self.save_birthdays()
                await message.add_reaction('✅')



            elif "list birthdays" in message.content:
                values = sorted(self.birthdays.items(), key=lambda p: p[1])
                print(values)
                message_to_send = ""
                for userID, date in values:
                    user = await self.fetch_user(userID)
                    message_to_send += self.birthdays[userID].strftime("%B %d") + " - " + user.display_name + "\n"
                
                if message_to_send != "":
                    await message.channel.send(message_to_send)

            # to look at if I want it later
            ''' if "embed" in message.content:
                 names=[str(i) for i in range(10)]
                names = '\n'.join(names)
                embedVar = discord.Embed(title="Commands", description="A list of commands I use", color=0x00ff00)
                embedVar.add_field(name="Command", value=names, inline=True)
                embedVar.add_field(name="Description", value="", inline=True)
                await message.channel.send(embed=embedVar)'''



        else:
            if "connect 4" in message.content.lower() or "connect4" in message.content.lower():
                await message.delete()
                return

            # if we should ignore the user
            if message.author.id in self.ignore_list:
                return
            

            # if its a link ignore
            elif "http" in message.content:
                return 



             
            else:
                message_to_send = ""
                            # open AI
                if message.author.id in self.useable:
                    prompt_to_send = "Human: Hello\nAi: Hello"+message.content[:110] + "\nAi:"
                    message_to_send = openai.Completion.create(engine="text-ada-001",
                    prompt=prompt_to_send, 
                    temperature=0.9,
                    max_tokens=25,
                    presence_penalty=0.6,
                    frequency_penalty=0.1,
                    stop=["Human:", "AI:"]
                ).choices[0].text

                # time checking
                roles = [y.name.lower() for y in message.author.roles]
                
                time_zone = None

                if "east coast" in roles:
                    time_zone = "EST"
                    offset = "-0500"
                
                elif "middle coast" in roles:
                    time_zone = "CT"
                    offset = "-0600"

                elif "west coast" in roles:
                    time_zone = "PST"
                    offset = "-0800"



                if time_zone == None: 
                    return

                found = re.findall("((?:0?1?\d|2[0-3]):(?:[0-5]\d)(?: )?(?:(?=am|AM|Am|pm|PM|Pm))?|(?:0?1?\d|2[0-3])(?: )?(?=am|AM|Am|pm|PM|Pm))(?:(am|AM|Am|pm|PM|Pm)?)", message.content)
                # found = re.findall("((?:0?1?\d|2[0-3]):(?:[0-5]\d)(?: ?)|24:00(?: ?)|(?<!\d)[0-9]{1,2}(?: ?)(?=[apAP]))(?:(?<=[\d ])(am|AM|Am|pm|PM|Pm)\s?)?", message.content)
                print(found)
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
                
                if (message_to_send != ""):  
                    await message.channel.send(message_to_send)
    

    # reddit get top post from sub reddit (jank)
    '''@tasks.loop(hours=24)
    async def called_once_a_day(self,):
        # delay a raondom number of time to avoid detection
        sleep(random.randint(0,600))
        sub_reddit="me_irl"
        user_agent = {'User-agent': 'Mozilla/5.0'}

        # get top post of the day thing
        x = requests.get('https://old.reddit.com/r/'+sub_reddit+'/top/?sort=top&t=day', headers = user_agent)
        code=x.text[x.text.find("thing id-t3")+12:x.text.find("thing id-t3")+18]

        # sleep to avoid sus
        sleep(1)
        x = requests.get('https://old.reddit.com/r/'+sub_reddit+'/comments/'+code+'/'+sub_reddit+'/', headers = user_agent)
        link = x.text[x.text.find("post-link")-54:x.text.find("post-link")-19]


        message_channel = self.get_channel(797314600759722004)
        # print(f"Got channel {message_channel}")
        # await message_channel.send("Daily meme generated by GPT3")
        await message_channel.send(link + " meme of the day")'''

    @tasks.loop(hours=24)
    async def called_once_a_day(self,):
        message_channel = self.get_channel(655557249640562731)
        current = datetime.datetime.now().date()
        for userID in self.birthdays:
            if current == self.birthdays[userID].date().replace(year=current.year):    
                await message_channel.send("@everyone Its <@"+str(userID)+">'s Birthday! Happy Birthday!", allowed_mentions = discord.AllowedMentions(everyone = True)) 
        
    def listRoles(self, message):
        return [role for role in message.guild.roles if role.color.value == 16777215] 
         
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(local_secrets['token'])
