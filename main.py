from threading import Thread
from cwebsocket import initialize_websocket
from schema import create_database
from os import environ
from commands import bot


def run_bot():
    bot.run(environ['DISCORD_TOKEN'])


def main():
    create_database()
    Thread(target=initialize_websocket, args=[]).start()
    t2 = Thread(target=run_bot, args=())
    t2.start()
    t2.join()


if __name__ == '__main__':
    main()
