import discord
from dotenv import load_dotenv
import os

load_dotenv()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(994651198948909094)
    await channel.send('hello')

@client.event
async def on_message(message):
    print(message)
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(os.environ["DISCORD_TOKEN"])
