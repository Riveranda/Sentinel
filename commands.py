from utils import JSONUTILS
from Dbutily import *
from discord.ext import commands
from Mybot import MyBot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import discord
from discord.ext import commands

description = "An early warning system for Eve online."
intents = discord.Intents.default()
intents.message_content = True

engine = create_engine('sqlite:///database.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
bot: commands.Bot = MyBot(command_prefix='!',
                          description=description, intents=intents)
bot.session = session

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (IUD: {bot.user.id})")
    print("-------")


@bot.command()
async def watch(ctx, system: str):
    if add_system_to_watch(session, ctx, system):
        await ctx.send(f'System: {system} added to watch list!')
    else:
        await ctx.send(f'System: {system} is already being watched!')


@bot.command()
async def ignore(ctx: commands.Context, system: str):
    if JSONUTILS.remove_system(system):
        await ctx.send(f'System: {system} removed from watch list!')
    else:
        await ctx.send(f"System: {system} not being watched: Add with !watch system.")


@bot.command()
async def setchannel(ctx: commands.Context):
    if not is_server_channel_set(session, ctx.guild.id):
        await ctx.send(f"Channel set to: {ctx.channel.name}. Notifications will now appear in {ctx.channel.name}")
    else:
        await ctx.send(f"Channel moved to: {ctx.channel.name}. Notifications will now appear in {ctx.channel.name}")
    update_server_channel(session, ctx)


@bot.command()
async def stop(ctx: commands.Context):
    update_server_muted(session, ctx, True)
    await ctx.send(f"Stopped!")


@bot.command()
async def start(ctx: commands.Context):
    update_server_muted(session, ctx, False)
    await ctx.send(f"Started!")
