from keep_alive import keep_alive
import discord
import os
import requests
import json
from discord.ext import commands


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

def get_joke():
  response = requests.get("https://official-joke-api.appspot.com/jokes/random")
  json_data = json.loads(response.text)
  setup = json_data['setup']
  punchline = json_data['punchline']
  return(setup+"\n"+"Ans - "+ punchline)

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
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)
  
  prefixes[str(ctx.guild.id)] = prefix

  with open('prefixes.json', 'w') as f:
    json.dump(prefixes, f, indent=4)
  
  await ctx.send(f'Prefix changed to {prefix}')

@client.event
async def on_message(message):
  await client.process_commands(message)
  
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)
  prefix = prefixes[str(message.guild.id)]

  if message.author == client.user:
    return

  if message.content.startswith(prefix+'inspire'):
    quote = get_quote()
    await message.channel.send(quote)

  if message.content.startswith(prefix+'joke'):
    joke = get_joke()
    await message.channel.send(joke)

  if message.content.startswith(prefix+'hello'):
    await message.channel.send('Hello!')
  
  if message.content.startswith(prefix+'help'):
    file = open("help.txt", "r")
    file = file.read()
    await message.channel.send(file)

keep_alive()
client.run(os.getenv('TOKEN'))