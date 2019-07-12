import re
import datetime
import json
from static import QA_FILE
from wit import Wit

access_token = "IMR2QK2LRAF4KEIPWGK72UOYALF366FG"
client = Wit(access_token)


def wit_mess(input):
    try:
        return client.message(input)
    except:
        return {'entities': {}}

def write_json(filename, js):
    with open(filename, 'w',  encoding='utf8') as f:
        json.dump(js, f)


def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def check_start_question(input, questions):
    for q in questions:
        if len(re.findall(q["text"], input)) != 0:
            return True
    return False


def check_choose(input, chooses):
    for choose in chooses:
        rg = choose["text"]
        if rg.startswith("WIT"):
            mch = rg.split("|", 1)[1]
            resp = wit_mess(input)
            entities = resp["entities"]
            if 'intent' in entities:
                intent = entities['intent'][0]['value']
            else:
                continue
            print("intent:", intent, mch)
            if intent == mch:
                return True
        elif len(re.findall(rg, input)) != 0:
            return True
    return False


def check_number_int(x):
    x = str(x)
    if x == "":
        return False
    for c in x:
        if not c.isdecimal():
            return False
    return True


def check_string(input):
    return input is not None and len(input) != 0


def check_date(input):
    try:
        datetime.datetime.strptime(input, '%d-%m-%Y')
    except ValueError:
        try:
            datetime.datetime.strptime(input, '%d/%m/%Y')
        except ValueError:
            try:
                datetime.datetime.strptime(input, '%d,%m,%Y')
            except ValueError:
                try:
                    datetime.datetime.strptime(input, '%Y,%m,%d')
                except ValueError:
                    return False
    return True


def check_time(input):
    return len(re.findall("....-..-..T..:..:.......+..:..", input)) != 0
    # return True


def get_time(itime):
    return itime.split("T",1)[1]

def get_date(itime):
    return itime.split("T",1)[0]

def check_input_type(input, input_type):
    if input_type == "NUMBER":
        return check_number_int(input)
    if input_type == "ADDRESS":
        return check_string(input)
    if input_type == "DATE":
        return check_date(input)
    if input_type == "TIME":
        return check_time(input)
    return True


def extract_data(input, input_type):
    if input_type == "NUMBER":
        return input
    if input_type == "ADDRESS":
        return input
    if input_type == "DATE":
        resp = wit_mess(input)
        entities = resp["entities"]
        if 'datetime' not in entities:
            return input
        else:
            return entities['datetime'][0]['value'][0]['value']
    if input_type == "TIME":
        resp = wit_mess(input)
        entities = resp["entities"]
        if 'datetime' not in entities:
            return input
        else:
            return entities['datetime'][0]['values'][0]['value']
    return input


def try_answer(input):
    ljs = read_json(QA_FILE)
    for qa in ljs:
        print(qa["question"],"-----")
        if qa["question"] == input:
            return qa["answer"]
    return "NEW"

# print(client.message("ngày mai"))
