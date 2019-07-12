from concurrent import futures
import os
import uuid
import time
import json
from datetime import datetime
import traceback
import logging
logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s', level=logging.DEBUG)
from bot import Bot

import grpc

import chatbot_pb2
import chatbot_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class ChatBot(chatbot_pb2_grpc.ChatBotServicer):
    ERROR = -1
    SUCCESS = 200
    BOTS = [('bot_duoc', 'Chuyên viên dược phẩm'), ('bot_tongdai', 'Chuyên viên tổng đài')]

    def __init__(self):
        logging.info("ChatBot service started!")

    def ListBot(self, request, context):
        list_bot_response = chatbot_pb2.ListBotResponse()
        for code, name in ChatBot.BOTS:
            bot = chatbot_pb2.Bot(code=code, name=name)
            list_bot_response.bots.append(bot)
        return list_bot_response

    def ChatToBot(self, request_iterator, context):
        client_id = datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(uuid.uuid4())[:8]
        # Get config from first request
        request = next(request_iterator)
        # The first request must contain chatbot_config
        if request.chatbot_config is None:
            logging.error("{}\t{}".format(client_id, "First request must contain voicebot_config field!"))
            yield chatbot_pb2.ChatBotResponse(
                status=chatbot_pb2.Status(
                    code=ChatBot.ERROR, 
                    message="First request must contain chatbot_config field!"))
            
            return
        # Check if bot are available
        bot_code = None
        for code, name in ChatBot.BOTS:
            if code == request.chatbot_config.bot_code:
                bot_code = code
                break
        if bot_code is None:
            logging.error("{}\t{}".format(client_id, "Unknown bot code {}".format(request.chatbot_config.bot_code)))
            yield chatbot_pb2.ChatBotResponse(
                status=chatbot_pb2.Status(
                    code=ChatBot.ERROR, 
                    message="Unknown bot code {}".format(request.chatbot_config.bot_code)))
            return
        # Push request for coressponding bot
        logging.info("{}\tChat to {}".format(client_id, bot_code))
        if bot_code == 'bot_duoc':
            chattobot_response_iterator = self.ChatToBot_Duoc(request_iterator)
        elif bot_code == 'bot_tongdai':
            chattobot_response_iterator = self.ChatToBot_TongDai(request_iterator)
        for chattobot_response in chattobot_response_iterator:
            yield chattobot_response
        logging.info("{}\tFinish chat!".format(client_id))

    def ChatToBot_Duoc(self, request_iterator):
        bot_duoc = Bot()
        for request in request_iterator:
            #### Process Chatbot HEREEEEEE ####
            text_ask = request.text

            text_ask = bot_duoc.next_sentence(text_ask)
            resp = ""
            for text in text_ask:
                resp = resp + text + "."
            resp = resp.replace("..",".")
            text_response = "Dược | " + resp
            ###################################
            yield chatbot_pb2.ChatBotResponse(
                status=chatbot_pb2.Status(
                    code=ChatBot.SUCCESS,
                    message="success"),
                text=text_response)

    def ChatToBot_TongDai(self, request_iterator):
        for request in request_iterator:
            #### Process Chatbot HEREEEEEE ####
            text_ask = request.text
            text_response = "Tổng đài | " + text_ask
            ###################################
            yield chatbot_pb2.ChatBotResponse(
                status=chatbot_pb2.Status(
                    code=ChatBot.SUCCESS,
                    message="success"),
                text="1 | " + text_response)
            yield chatbot_pb2.ChatBotResponse(
                status=chatbot_pb2.Status(
                    code=ChatBot.SUCCESS,
                    message="success"),
                text="2 | " + text_response)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), maximum_concurrent_rpcs=10, options=(('grpc.so_reuseport', 0),))
    chatbot_pb2_grpc.add_ChatBotServicer_to_server(ChatBot(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
