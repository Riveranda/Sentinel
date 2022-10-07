import websocket
import time
from json import loads

message_queue = []


def on_message(ws, message):
    json_obj = loads(message)
    # if json_obj["victim"]["corporation_id"] == 93593825:
    message_queue.append(f"{json_obj['zkb']['url']}")
    #print(dumps(loads(message), indent=4))
    print("Kill recieved")


def on_error(ws, error):
    time.sleep(5)
    initialize_websocket()


def on_close(ws):
    print("Closed")


def on_open(ws):
    ws.send('{"action":"sub","channel":"killstream"}')


def initialize_websocket():

    ws = websocket.WebSocketApp("wss://zkillboard.com/websocket/",
                                on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever()
