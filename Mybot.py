from discord.ext import tasks
from CWebSocket import message_queue
from discord.ext import commands
from Dbutily import *


class MyBot(commands.Bot):
    session = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocker = False

    @tasks.loop(seconds=1)
    async def background_task(self):
        if self.blocker or len(message_queue) == 0:
            return
        self.blocker = True

        while (len(message_queue) != 0):
            message = message_queue.pop(0)
            for guild in self.guilds:
                if is_server_channel_set(self.session, guild.id) and not is_server_muted(self.session, guild.id):
                    self.blocker = True
                    channelid = get_channel_id_from_guild_id(
                        self.session, guild.id)
                    print(f"Channel ID: {channelid}")
                    if channelid == None:
                        continue
                    channel = self.get_channel(channelid)
                    await channel.send(message)

        self.blocker = False

    async def setup_hook(self):
        self.background_task.start()

    @background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()
