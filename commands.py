from dbutility import *
from discord.ext import commands
from mybot import MyBot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import discord

description = "An early warning system for Eve online."
intents = discord.Intents.default()
intents.message_content = True

engine = create_engine('sqlite:///database.db', echo=False)
Session_factory = sessionmaker(bind=engine)
Session = scoped_session(Session_factory)

bot: commands.Bot = MyBot(command_prefix='/',
                          description=description, intents=intents)
tree = bot.tree


@tree.command(name="watchalliance", description="Add a filter for an alliance.")
async def watchalliance(interaction: discord.Interaction, alliance: str):
    session = Session()

    def close():
        Session.remove()

    if not is_ally_recorded(alliance, session):
        if alliance.isdigit():
            if not add_new_ally_by_id(int(alliance), session):
                close()
                await interaction.response.send_message(f"Invalid Alliance ID: {int(alliance)}")
                return
        else:
            close()
            await interaction.response.send_message(r"Alliance not in database. Please try adding by id: '{/watchalliance {alliance_id}'")
            return
    added, already_watched, ally_name = add_object_to_watch(
        interaction, session, alliance, Alliances)
    if already_watched:
        close()
        await interaction.response.send_message(f"Alliance: {ally_name} is already being watched!")
        return
    elif added:
        close()
        await interaction.response.send_message(f"Alliance: {ally_name} added to watch list!")
        return
    close()
    await interaction.response.send_message(f"Unknown Alliance, try adding by id or check your spelling.")


@tree.command(name="watchcorp", description="Add a filter for a corporation.")
async def watchcorp(interaction: discord.Interaction, corp: str):
    def close():
        Session.remove()
    session = Session()
    if (not is_corp_recorded(corp, session)):
        print(int(corp))
        if corp.isdigit():
            if not add_new_corp_by_id(int(corp), session):
                close()
                await interaction.response.send_message(f"Invalid Corporation Id: {int(corp)}")
                return
        else:
            close()
            await interaction.response.send_message(r"Corporation not in database. Please try adding by id: '/watchcorp {corporation_id}'")
            return
    added, already_watched, corp_name = add_object_to_watch(
        interaction, session, corp, Corporations)
    if already_watched:
        close()
        await interaction.response.send_message(f"Corporation: {corp_name} is already being watched!")
        return
    elif added:
        close()
        await interaction.response.send_message(f"Corporation: {corp_name} added to watch list!")
        return
    close()
    await interaction.response.send_message(f"Unknown Corporation, try adding by id or check your spelling.")


@tree.command(name="watch", description="Filter for a system, region, or constellation.")
async def watch(interaction: discord.Interaction, obj: str):
    session = Session()

    def close():
        Session.remove()

    added, already_watched, system_name = add_object_to_watch(
        interaction, session, obj, Systems)
    if already_watched:
        close()
        await interaction.response.send_message(f"System: {system_name} is already being watched!")
        return
    elif added:
        close()
        await interaction.response.send_message(f"System: {system_name} added to watch list!")
        return

    added, already_watched, constellation_name = add_object_to_watch(
        interaction, session, obj, Constellations)
    if already_watched:
        close()
        await interaction.response.send_message(f"Constellation: {constellation_name} is already being watched!")
        return
    elif added:
        close()
        await interaction.response.send_message(f"Constellation: {constellation_name} added to watch list!")
        return

    added, already_watched, region_name = add_object_to_watch(
        interaction, session, obj, Regions)
    if already_watched:
        close()
        await interaction.response.send_message(f"Region: {region_name} is already being watched!")
        return
    elif added:
        close()
        await interaction.response.send_message(f"Region: {region_name} added to watch list!")
        return
    close()
    await interaction.response.send_message(f"Unknown celestial object, check your spelling.")


@tree.command(name="ignorealliance", description="Remove an alliance from the filters")
async def ignorealliance(interaction: discord.Interaction, alliance: str):
    session = Session()

    def close():
        Session.remove()

    if not is_ally_recorded(alliance, session):
        if alliance.isdigit():
            if not add_new_ally_by_id(int(alliance), session):
                close()
                await interaction.response.send_message(f"Invalid Alliance Id: {int(alliance)}")
                return
        else:
            close()
            await interaction.response.send_message(r"Alliance not in database. Please try by id: '/ignorealliance {alliance_id}'")
            return
    removed, not_watched, ally_name = remove_object_from_watch(
        interaction, session, alliance, Alliances)
    if removed:
        close()
        await interaction.response.send_message(f"Alliance: {ally_name} removed from watch list!")
        return
    elif not_watched:
        close()
        await interaction.response.send_message(f"Alliance: {ally_name} is not being watched!")
        return
    close()
    await interaction.response.send_message(f"Unknown Alliance, try removing by ID or check your spelling.")


@tree.command(name="ignorecorp", description="Remove a Corporation from the filters")
async def ignorealliance(interaction: discord.Interaction, corp: str):
    session = Session()

    def close():
        Session.remove()

    if not is_corp_recorded(corp, session):
        if corp.isdigit():
            print("adding")
            if not add_new_corp_by_id(int(corp), session):
                close()
                await interaction.response.send_message(f"Invalid Corporation Id: {int(corp)}")
                return
        else:
            close()
            await interaction.response.send_message(r"Corporation not in database. Please add by id: '/ignore {corporation_id]}'")
            return
    removed, not_watched, corp_name = remove_object_from_watch(
        interaction, session, corp, Corporations)
    if removed:
        close()
        await interaction.response.send_message(f"Corporation: {corp_name} removed from watch list!")
        return
    elif not_watched:
        close()
        await interaction.response.send_message(f"Corporation: {corp_name} is not being watched!")
        return
    close()
    await interaction.response.send_message(f"Unknown Corporation, try removing by ID or check your spelling.")


@tree.command(name="ignore", description="Remove the filter for a system, region, or constellation.")
async def ignore(interaction: discord.Interaction, obj: str):
    session = Session()

    def close():
        Session.remove()

    removed, not_watched, system_name = remove_object_from_watch(
        interaction, session, obj, Systems)
    if removed:
        close()
        await interaction.response.send_message(f"System: {system_name} removed from watch list!")
        return
    if not_watched:
        close()
        await interaction.response.send_message(f"System: {system_name} is not being watched!")
        return

    removed, not_watched, constellation_name = remove_object_from_watch(
        interaction, session, obj, Constellations)
    if removed:
        close()
        await interaction.response.send_message(f"Constellation: {constellation_name} removed from watch list!")
        return
    if not_watched:
        close()
        await interaction.response.send_message(f"Constellation: {constellation_name} is not being watched!")
        return

    removed, not_watched, region_name = remove_object_from_watch(
        interaction, session, obj, Regions)
    if removed:
        close()
        await interaction.response.send_message(f"Region: {region_name} removed from watch list!")
        return
    if not_watched:
        close()
        await interaction.response.send_message(f"Region: {region_name} is not being watched!")
        return
    close()
    await interaction.response.send_message(f"Unknown cellestial object, check your spelling.")


@tree.command(name="watchall", description="Remove all filters. Recieve all killmails.")
async def watchall(interaction: discord.Interaction):
    session = Session()
    set_filter_to_all(interaction.guild.id, session)
    Session.remove()
    await interaction.response.send_message(f"All filters removed! Watching all kills.")


@tree.command(name="setchannel", description="Set the channel for the killstream.")
async def setchannel(interaction: discord.Interaction):
    session = Session()
    channel = bot.get_channel(interaction.channel_id)
    if not is_server_channel_set(interaction.guild.id, session):
        await interaction.response.send_message(f"Channel set to: {channel.name}. Notifications will now appear in {channel.name}")
    else:
        await interaction.response.send_message(f"Channel moved to: {channel.name}. Notifications will now appear in {channel.name}")
    update_server_channel(interaction, session)
    Session.remove()


@bot.event
async def on_guild_join(guild):
    await tree.sync(guild=guild.id)
    session = Session()
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            create_new_guild(channel.id, guild, session)
    Session.remove()


@tree.command(name="stop", description="Stop the killstream.")
async def stop(interaction: discord.Interaction):
    session = Session()
    update_server_muted(session, interaction, True)
    Session.remove()
    await interaction.response.send_message(f"Stopped!")


@tree.command(name="start", description="Start the killstream.")
async def start(interaction: discord.Interaction):
    session = Session()
    update_server_muted(session, interaction, False)
    Session.remove()
    await interaction.response.send_message(f"Started!")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (IUD: {bot.user.id})")
    print("-------")
    await tree.sync()
