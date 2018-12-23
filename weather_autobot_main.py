import itchat
import re
from itchat.content import *
from get_weather_from_api import *

def weather_main(userName, theCity=None,zip=63017):
    if theCity=='zip mode':
        weather_text_list = get_weather_by_zip(zip)
    else:
        weather_text_list = get_weather_by_city(theCity)

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

# 如果对方发的是文字，则我们给对方回复以下的东西
@itchat.msg_register([TEXT])
def text_reply(msg):
    city = extract_cityname(msg['Text'])
    weather_main(msg['FromUserName'], city)

@itchat.msg_register([TEXT], isGroupChat=True)
def text_reply(msg):
    if not msg['User']['NickName'] == '咱们这一家子':
        return None
    else:
        city = extract_cityname(msg['Text'])
        weather_main(msg['FromUserName'], city)

itchat.auto_login(hotReload=True)
itchat.run()
