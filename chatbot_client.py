from __future__ import print_function
import sys
import traceback
import logging
logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s', level=logging.INFO)
from static import FINISH_CONVERSATION
import grpc
import time

import chatbot_pb2
import chatbot_pb2_grpc

CONNECTED = True
TEXTS = [
    'alo',
    'con mình gọi',
    'okie'
]


def auto_text(bot_code):
    global CONNECTED, TEXTS
    yield chatbot_pb2.ChatBotRequest(chatbot_config=chatbot_pb2.ChatBotConfig(bot_code=bot_code))
    while True:
    # for text in TEXTS:
        text = sys.stdin.readline()
        text = text.replace("\n", "")
        print("Me: " + text)
        yield chatbot_pb2.ChatBotRequest(text=text)
        time.sleep(2)

def run():
    global CONNECTED
    
    with grpc.insecure_channel('localhost:50051') as channel:
        chatbot_stub = chatbot_pb2_grpc.ChatBotStub(channel)

        # Get list bot
        print("### chatbot_stub.ListBot")
        list_bot_response = chatbot_stub.ListBot(chatbot_pb2.ListBotRequest())
        for bot in list_bot_response.bots:
            print(bot.code, bot.name)
        print("-----------------------")

        # Talk to bot from input
        print("### chatbot_stub.ListBot")
        input_iterator = auto_text('bot_duoc')
        # input_iterator = auto_text('bot_tongdai')
        chatbot_response_iterator = chatbot_stub.ChatToBot(input_iterator)
        for chatbot_response in chatbot_response_iterator:
            if chatbot_response.status.code == 200:
                time.sleep(0.1)
                print("Bot: " + chatbot_response.text)

if __name__ == '__main__':
    run()