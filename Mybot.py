from discord.ext import tasks
from CWebSocket import message_queue, does_msg_match_guild_watchlist
from discord.ext import commands
from dbutility import *


class MyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocker = False

    @tasks.loop(seconds=1)
    async def background_task(self):
        if self.blocker or len(message_queue) == 0:
            return

        self.blocker = True

        from commands import Session
        session = Session()

        # Cache the ready status of the guild to prevent redunant

        @lru_cache(maxsize=100)
        def check_guild_status(guild_id: int):
            return is_server_channel_set(guild_id, session) and not is_server_muted(session, guild_id)

        # Cache the channel id to prevent redundant queries
        @lru_cache(maxsize=100)
        def get_channel_id(guild_id: int):
            return get_channel_id_from_guild_id(session, guild_id)

        while (len(message_queue) != 0):
            message = message_queue.pop(0)
            for guild in self.guilds:
                if check_guild_status(guild.id):
                    if not does_msg_match_guild_watchlist(message, guild.id, session):
                        continue
                    channelid = get_channel_id(guild.id)
                    if channelid == None:
                        continue
                    channel = self.get_channel(channelid)
                    await channel.send(message['zkb']['url'])

        self.blocker = False
        Session.remove()

    async def setup_hook(self):
        self.background_task.start()

    @background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()
