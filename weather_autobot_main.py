import itchat
from itchat.content import *
from get_weather_from_api import *
import pandas as pd

with open('api_key.txt', 'r') as f:
    ak = f.readlines()
ak = [x.strip() for x in ak]

def weather_main(userName,theCity='St. Louis',zip=63017,ak0=None,ak1=None):
    if theCity=='zip mode':
        weather_text_list = get_weather_by_zip(zip,ak1)
    elif theCity:
        weather_text_list = get_weather_by_city(theCity,ak0,ak1)
    else:
        return print('No City found')
    for weather_text in weather_text_list:
        itchat.send(weather_text, toUserName=userName)
    print('succeed')

def extract_cityname(txt):
    if txt == '天气':
        city = 'zip mode'
        return city
    elif '天气' in txt:
        txt = txt.replace('天气', '')
        city = txt.replace("+",'')
        #city = ''.join(e for e in txt if e.isalnum()) #remove all the special character
        return city.strip()
    else:
        return None

# 如果对方发的是文字，则我们给对方回复以下的东西
@itchat.msg_register([TEXT])
def text_reply(msg):
    city = extract_cityname(msg['Text'])
    if city:
        weather_main(msg['FromUserName'], city, ak0=ak[0], ak1=ak[1])

@itchat.msg_register([TEXT], isGroupChat=True)
def text_reply(msg):
    if not msg['User']['NickName'] == '咱们这一家子':
        return None
    else:
        city = extract_cityname(msg['Text'])
        if city:
            weather_main(msg['FromUserName'], city, ak0=ak[0], ak1=ak[1])

itchat.auto_login(hotReload=True)
itchat.run()
