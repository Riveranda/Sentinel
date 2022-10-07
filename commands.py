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
async def watch(ctx, obj: str):
    added, already_watched, system_name = add_system_to_watch(ctx.guild.id, ctx, session, obj)
    if already_watched:
        await ctx.send(f"System: {system_name} is already being watched!")
        return
    elif added:
        await ctx.send(f"System: {system_name} added to watch list!")
        return

    added, already_watched, constellation_name = add_constellation_to_watch(ctx.guild.id, ctx, session, obj)
    if already_watched:
        await ctx.send(f"Constellation: {constellation_name} is already being watched!")
        return
    elif added:
        await ctx.send(f"Constellation: {constellation_name} added to watch list!")
        return
    
    added, already_watched, region_name = add_region_to_watch(ctx.guild.id, ctx, session, obj)
    if already_watched:
        await ctx.send(f"Region: {region_name} is already being watched!")
        return
    elif added:
        await ctx.send(f"Region: {region_name} added to watch list!")
        return
    
    # added, already_watched, corp_name = add_corp_to_watch(ctx.guild.id, ctx, session, obj)
    # if already_watched:
    #     await ctx.send(f"Corporation: {corp_name} is already being watched!")
    #     return
    # elif added:
    #     await ctx.send(f"Corporation: {corp_name} added to watch list!")
    #     return


    

@bot.command()
async def ignore(ctx, obj: str):
    removed, not_watched, system_name = remove_system_from_watch(ctx.guild.id, ctx, session, obj)
    if removed:
        await ctx.send(f"System: {system_name} removed from watch list!")
        return
    if not_watched:
        await ctx.send(f"System: {system_name} is not being watched!")
        return

    removed, not_watched, constellation_name = remove_constellation_from_watch(ctx.guild.id, ctx, session, obj)
    if removed:
        await ctx.send(f"Constellation: {constellation_name} removed from watch list!")
        return
    if not_watched:
        await ctx.send(f"Constellation: {constellation_name} is not being watched!")
        return

    removed, not_watched, region_name = remove_region_from_watch(ctx.guild.id, ctx, session, obj)
    if removed:
        await ctx.send(f"Region: {region_name} removed from watch list!")
        return
    if not_watched:
        await ctx.send(f"Region: {region_name} is not being watched!")
        return
    
    
@bot.command()
async def setchannel(ctx: commands.Context):
    if not is_server_channel_set(session, ctx.guild.id):
        await ctx.send(f"Channel set to: {ctx.channel.name}. Notifications will now appear in {ctx.channel.name}")
    else:
        await ctx.send(f"Channel moved to: {ctx.channel.name}. Notifications will now appear in {ctx.channel.name}")
    update_server_channel(session, ctx)

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            create_new_guild(channel.id, guild, session)

@bot.command()
async def stop(ctx: commands.Context):
    update_server_muted(session, ctx, True)
    await ctx.send(f"Stopped!")


@bot.command()
async def start(ctx: commands.Context):
    update_server_muted(session, ctx, False)
    await ctx.send(f"Started!")
