from contextvars import Context
from dbutility import *
from discord.ext import commands
from mybot import MyBot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from discord.ext import commands
import discord

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
async def watch(ctx: commands.Context, obj: str):
    if "alliance:" in obj:
        ally_str = obj.replace("alliance:", "")
        if not is_ally_recorded(ally_str, session):
            if ally_str.isdigit():
                add_new_ally_by_id(int(ally_str), session)
            else:
                await ctx.send(f"Alliance not in database. Please add by id: \"!watch alliance:[alliance_id]\"")
                return
        added, already_watched, ally_name = add_ally_to_watch(ctx.guild.id, ctx, session, ally_str)
        if already_watched:
            await ctx.send(f"Alliance: {ally_name} is already being watched!")
            return
        elif added:
            await ctx.send(f"Alliance: {ally_name} added to watch list!")
            return
    if "corp:" in obj:
        ally_str = obj.replace("corp:", "")
        if not is_corp_recorded(ally_str, session):
            if ally_str.isdigit():
                add_new_corp_by_id(int(ally_str), session)
            else:
                await ctx.send(f"Corporation not in database. Please add by id: \"!watch corp:[corporation_id]\"")
                return
        added, already_watched, ally_name = add_corp_to_watch(ctx.guild.id, ctx, session, ally_str)
        if already_watched:
            await ctx.send(f"Corporation: {ally_name} is already being watched!")
            return
        elif added:
            await ctx.send(f"Corporation: {ally_name} added to watch list!")
            return

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


@bot.command()
async def ignore(ctx : commands.Context, obj: str):
    if "corp:" in obj:
        corp_str = obj.replace("corp:", "")
        if not is_corp_recorded(corp_str, session):
            if corp_str.isdigit():
                add_new_corp_by_id(int(corp_str), session)
            else:
                await ctx.send(f"Corporation not in database. Please add by id: \"!ignore corp:[corporation_id]\"")
                return
        removed, not_watched, corp_name = remove_corp_from_watch(ctx.guild.id, ctx, session, corp_str)
        if removed:
            await ctx.send(f"Corporation: {corp_name} removed from watch list!")
            return
        elif not_watched:
            await ctx.send(f"Corporation: {corp_name} is not being watched!")
            return
    if "alliance:" in obj:
        ally_str = obj.replace("alliance:", "")
        if not is_ally_recorded(ally_str, session):
            if ally_str.isdigit():
                add_new_ally_by_id(int(ally_str), session)
            else:
                await ctx.send(f"Alliance not in database. Please add by id: \"!ignore alliance:[alliance_id]\"")
                return
        removed, not_watched, ally_name = remove_ally_from_watch(ctx.guild.id, ctx, session, ally_str)
        if removed:
            await ctx.send(f"Alliance: {ally_name} removed from watch list!")
            return
        elif not_watched:
            await ctx.send(f"Alliance: {ally_name} is not being watched!")
            return
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
async def watchall(ctx: commands.Context):
    set_filter_to_all(ctx.guild.id, session)
    await ctx.send(f"All filters removed! Watching all kills.")
    
    
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
