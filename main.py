import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Bot online como {bot.user}')

async def main():
    async with bot:
        await bot.load_extension('cogs.content')
        await bot.load_extension('cogs.gerenciar')
        await bot.start(os.getenv('TOKEN'))

asyncio.run(main())