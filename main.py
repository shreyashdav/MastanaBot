from keep_alive import keep_alive
import discord
import os, html, datetime
import requests
import json, random
from discord.ext import commands
from dateutil import parser
import asyncio # To get the exception

eight_ball = [ "It is certain", "It is decidedly so", "Without any doubt", "Yes, definitely", "Have you lost your mind!",
               "You may rely on it", "As I see it, yes", "Most Likely", "Outlook Good",
               "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later","My sources say yes",
               "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
               "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very Doubtful",
			   "Don't even think of it", "It's never gonna happen", "I doubt that", "Are you stupid", "Damn! No", "Very doubtful",
			   "Not just no, hell no!", "Sure thing", "Maybe not", "Count on it", "The Universe says maybe",
			   "I don't see why not", "The future looks good for you", "That's for sure", "Maybe", "There's a chance", "Certainly!",
			   "Keep doing what you're doing and it'll happen", "No!", "Yes!", "All depends on if you've been good for Santa this year",
			   "Not in this lifetime", "Someday, but not today","Right after you hit the lottery", "Don't think so"]

def get_prefix(client, message):
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)
  
  return prefixes[str(message.guild.id)]

# client = discord.Client()
client = commands.Bot(command_prefix=get_prefix, help_command=None)

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def get_tf(amt, diff):
  if diff is None:
    if amt is None:
      response = requests.get("https://opentdb.com/api.php?amount=1&type=boolean")
    else:
      response = requests.get("https://opentdb.com/api.php?amount="+str(amt)+"&type=boolean")
  elif amt is None:
    response = requests.get("https://opentdb.com/api.php?amount=1&type=boolean&difficulty="+diff)
  else:
    response = requests.get("https://opentdb.com/api.php?amount="+str(amt)+"&type=boolean&difficulty="+diff)
    
  json_data = json.loads(response.text)
  category = json_data['results'][0]['category']
  difficulty = str(json_data['results'][0]['difficulty']).capitalize()
  question = html.unescape(str(json_data['results'][0]['question']))
  correct_answer = json_data['results'][0]['correct_answer']
  tf = {"answer":correct_answer,"question":"""Difficulty - {}
Category - {}
Question - {}""".format(str(difficulty), str(category), str(question))}
  return(tf)
  
  pass

def get_mcq():
  pass

def get_topic():
  with open("topics.txt", "r") as f:
    f = f.read().splitlines()
    topic = random.choice(f)
    return topic

def get_joke():
  response = requests.get("https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,sexist,explicit")
  json_data = json.loads(response.text)
  if json_data['type'] == "twopart":
    setup = json_data['setup']
    delivery = json_data['delivery']
    return(setup+"\n"+"Punchline - "+ delivery)
  else:
    joke = json_data['joke']
    return joke

def get_meme():
  response = requests.get("https://meme-api.herokuapp.com/gimme")
  json_data = json.loads(response.text)
  url = json_data['url']
  title = json_data['title']
  embed = discord.Embed(
                title=str(title),
                color=discord.Colour.gold()
            )
  embed.set_image(url=url)
  return embed

def get_action(action):
  response = requests.get("https://api.waifu.pics/sfw/"+action)
  json_data = json.loads(response.text)
  action_url = json_data['url']
  return(action_url)

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game('Fun Games'))
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_guild_join(guild):
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)
  prefixes[str(guild.id)] = '$'

  with open('prefixes.json', 'w') as f:
    json.dump(prefixes, f, indent=4)

@client.event
async def on_guild_remove(guild):
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)
  
  prefixes.pop(str(guild.id))

  with open('prefixes.json', 'w') as f:
    json.dump(prefixes, f, indent=4)

@client.command()
async def changeprefix(ctx, prefix):
  if ctx.message.author.guild_permissions.administrator:
    with open('prefixes.json', 'r') as f:
      prefixes = json.load(f)
    
    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
      json.dump(prefixes, f, indent=4)
    
    await ctx.send(f'Prefix changed to {prefix}')
  else:
    await ctx.send(f"Only admin can change the prefix")

@client.event
async def on_message(message):
  await client.process_commands(message)

  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)
  if str(prefixes[str(message.guild.id)]).isalpha():
    prefix = str(prefixes[str(message.guild.id)]).lower()
  else:
    prefix = str(prefixes[str(message.guild.id)])
  
  with open('afk.json', 'r') as f:
    afkdict = json.load(f)
  
  if str(str(message.author.id)+"_"+str(message.guild.id)) in afkdict:
    afkdict.pop(str(str(message.author.id)+"_"+str(message.guild.id)))
    with open('afk.json', 'w') as f:
      json.dump(afkdict, f, indent=4)
    await message.channel.send('You are no longer AFK', delete_after=2)
    return

  #check if mention is in afk dict
  for member in message.mentions: #loops through every mention in the message
    if member != message.author: #checks if mention isn't the person who sent the message
      if str(member.id)+"_"+str(message.guild.id) in afkdict: #checks if person mentioned is afk
        afkmsg = afkdict[str(member.id)+"_"+str(message.guild.id)] 
        msg = afkmsg['message'] #gets the message the afk user set
        dt_now = datetime.datetime.now()
        min_diff = (dt_now - parser.parse(afkmsg['timestamp'])) // datetime.timedelta(minutes=1)
        if min_diff == 0:
          timeago = "just now"
        elif min_diff == 1:
          timeago = str(min_diff)+" minute ago"
        elif min_diff > 1 and min_diff <60:
          timeago = str(min_diff)+" minutes ago"
        elif min_diff > 60:
          min_diff_2 = (parser.parse(afkmsg['timestamp']) - dt_now) // datetime.timedelta(hours=1)
          if min_diff_2 == 1:
            timeago = str(min_diff)+" hour ago"
          elif min_diff_2 > 1 and min_diff_2 < 60:
            timeago = str(min_diff)+" hours ago"
          elif min_diff_2 > 60:
            min_diff_3 = (parser.parse(afkmsg['timestamp']) - dt_now) // datetime.timedelta(hours=1)
            if min_diff_3 == 1:
              timeago = str(min_diff)+" day ago"
            else:
              timeago = str(min_diff)+" days ago"
        await message.channel.send(f":rocket: {member.name} is AFK: {msg} - {timeago}") #send message to the channel the message was sent to 
    # else:
    #   if str(member.id) in afkdict: #checks if person mentioned is afk
    #     afkdict.pop(str(message.author.id))
    #     with open('afk.json', 'w') as f:
    #       json.dump(afkdict, f, indent=4)
    #     await message.channel.send('You are no longer AFK')

  if message.author == client.user:
    return

  if message.content.lower().startswith(prefix+'inspire'):
    quote = get_quote()
    await message.channel.send(quote)

  if message.content.lower().startswith(prefix+'joke'):
    joke = get_joke()
    await message.channel.send(joke)


  if message.content.lower().startswith(prefix+'topic'):
    topic = get_topic()
    await message.channel.send(topic)

  if message.content.lower().startswith(prefix+'meme'):
    meme = get_meme()
    await message.channel.send(embed=meme)

  if message.content.lower().startswith(prefix+'tf'):
    tf_list = str(message.content)[1:].split(" ")
    if len(tf_list) == 1:
      if len(tf_list) == 1 and str(tf_list[0]).lower()=="tf":
        tf = get_tf(None,None)
    
#     elif len(tf_list) == 4:
#       if tf_list[0] == prefix+'tf' and str(tf_list[1]).lower()=="mul" and str(tf_list[2]).lower() in ['e', 'm', 'd'] and int(tf_list[3]) > 0 and int(tf_list[2]) <=5:
#         tf = get_tf(tf_list[3],tf_list[2])
#     else:  
#       await message.channel.send("""Please enter in following format: tf mul <difficulty> <count>.
# Count shouldn't be greater than 5""")
    
    await message.channel.send(tf["question"])

    # This will make sure that the response will only be registered if the following
    # conditions are met:
    def check(msg):
        return msg.author == message.author and msg.channel == message.channel and \
        msg.content.lower() in ["true", "t", "yes", "y", "haan", "ha","haa", "yea", "yep", "yeah", "yo", "nope", "na", "nu", "nuu", "nah", "naah", "naa", "false", "f", "nai", "nahi", "no", "n"]
    try:
      msg = await client.wait_for("message", check=check, timeout=15) # 30 seconds to reply
    except asyncio.TimeoutError:
      await message.channel.send("Sorry, you didn't reply in time!")

    if msg.content.lower() in ["true", "t", "yes", "y", "haan", "ha","haa", "yea", "yep", "yeah", "yo"]:
      if tf["answer"] == "True":
        await message.channel.send("Yay! You got that right")
      else:
        await message.channel.send("Oops, It's wrong. Correct answer is False")
    elif msg.content.lower() in ["nope", "na", "nu", "nuu", "nah", "naah", "naa", "false", "f", "nai", "nahi", "no", "n"]:
      if tf["answer"] == "False":
        await message.channel.send("Yay! You got that right")
      else:
        await message.channel.send("Oops, It's wrong. Correct answer is True")
    else:
      await message.channel.send("Please give valid answer")

  if message.content.lower().startswith(prefix+'afk'):
    content = str(message.content).lower().split(prefix,1)
    if len(str(content[1]).split(" "))==1:
      msg = "AFK"
    else:
      msg = str(content[1]).split(" ",1)
      msg = msg[1]
    #remove member from afk dict if they are already in it
    with open('afk.json', 'r') as f:
      afkdict = json.load(f)
    if str(message.author.id)+"_"+str(message.guild.id) in afkdict:
        afkdict.pop(str(message.author.id)+"_"+str(message.guild.id))
        with open('afk.json', 'w') as f:
          json.dump(afkdict, f, indent=4)
        await message.channel.send('You are no longer AFK', delete_after=2)
    else:
        afkdict[str(message.author.id)+"_"+str(message.guild.id)] = {"message": msg, "timestamp": str(datetime.datetime.now())}
        with open('afk.json', 'w') as f:
          json.dump(afkdict, f, indent=4)
        await message.channel.send(f":rocket: You are now AFK - {msg}")


  if message.content.lower().startswith(prefix+'help'):
    file = open("help.txt", "r")
    file = file.read()
    await message.channel.send(file)

  if message.content.lower().startswith(prefix+'8ball'):
    msg_w_prefix = str(message.content).lower().split(prefix,1)
    msg_list = str(msg_w_prefix[1]).split(" ")
    if len(msg_list) < 2:
      await message.channel.send("You forgot to ask your question")
    else:
      msg = random.choice(eight_ball)
      await message.channel.send(msg)
  
  if message.content.lower().startswith(prefix+'say'):
    msg = str(message.content).lower().split(prefix+'say',1)[1]
    await message.delete()
    await message.channel.send(msg)

  if message.content.lower().startswith(prefix+'pat'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('pat')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" pats "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)
  
  if message.content.lower().startswith(prefix+'cuddle'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('cuddle')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" cuddles "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'hug'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('hug')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" hugs "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'kiss'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('kiss')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" kissed "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'slap'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('slap')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" slaps "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'kill'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('kill')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" killed "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'nom'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('nom')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" ate "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'bite'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('bite')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" bites "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'lick'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('lick')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" licks "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'bully'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('bully')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" bullies "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'bonk'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('bonk')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" bonks "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)
    
  if message.content.lower().startswith(prefix+'poke'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('poke')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" pokes "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'yeet'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('yeet')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" yeets "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)
  
  if message.content.lower().startswith(prefix+'handhold'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('handhold')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" handholds "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'highfive'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('highfive')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" highfives "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'glomp'):
    if len(message.mentions) == 0:
      await message.channel.send("Please mention at least 1 user")
    else:
      action = get_action('glomp')
      list_mem = [x.name for x in message.mentions]
      embed = discord.Embed(
                title=str(message.author.name)+" glomps "+str(', '.join(map(str, list_mem)) ),
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)
  
  # Adding reactions
  if message.content.lower().startswith(prefix+'cry'):
      action = get_action('cry')
      embed = discord.Embed(
                title=str(message.author.name)+" is crying hard",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'awoo'):
      action = get_action('awoo')
      embed = discord.Embed(
                title=str(message.author.name)+" is doing awoo",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'smug'):
      action = get_action('smug')
      embed = discord.Embed(
                title=str(message.author.name)+" is giving smug reaction",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'blush'):
      action = get_action('blush')
      embed = discord.Embed(
                title=str(message.author.name)+" is blushing",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'smile'):
      action = get_action('smile')
      embed = discord.Embed(
                title=str(message.author.name)+" is smiling",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'wave'):
      action = get_action('wave')
      embed = discord.Embed(
                title=str(message.author.name)+" is waving",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'happy'):
      action = get_action('happy')
      embed = discord.Embed(
                title=str(message.author.name)+" is happy today",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'wink'):
      action = get_action('wink')
      embed = discord.Embed(
                title=str(message.author.name)+" winks",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'dance'):
      action = get_action('dance')
      embed = discord.Embed(
                title=str(message.author.name)+" is dancing",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

  if message.content.lower().startswith(prefix+'cringe'):
      action = get_action('cringe')
      embed = discord.Embed(
                title=str(message.author.name)+" giving cringe reaction",
                color=discord.Colour.gold()
            )
      embed.set_image(url=action)
      await message.channel.send(embed=embed)

keep_alive()
client.run(os.getenv('TOKEN'))