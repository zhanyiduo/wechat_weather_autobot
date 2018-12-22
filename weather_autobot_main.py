import itchat
import re
from itchat.content import *
from get_weather_from_api import *

def weather_main(userName, theCity=None,zip=63017):
    if theCity==None:
        weather_text_list = get_weather_by_zip(zip)
    else:
        weather_text_list = get_weather_by_city(theCity)

    for weather_text in weather_text_list:
        itchat.send(weather_text, toUserName=userName)
    print('succeed')

# 如果对方发的是文字，则我们给对方回复以下的东西
@itchat.msg_register([TEXT])
def text_reply(msg):
    match1 = '天气' in msg['Text']
    match2 = "+" in msg['Text']
    if (match1) & (not match2):
        weather_main(msg['FromUserName'])
    elif match1 & match2:
        city = msg['Text'][msg['Text'].find("+")+1:]
        weather_main(msg['FromUserName'], city)

@itchat.msg_register([TEXT], isGroupChat=True)
def text_reply(msg):
    if not msg['User']['NickName'] == '咱们这一家子':
        return None
    else:
        match1 = '天气' in msg['Text']
        match2 = "+" in msg['Text']
        if (match1) & (not match2):
            weather_main(msg['FromUserName'])
        elif match1 & match2:
            city = msg['Text'][msg['Text'].find("+")+1:]
            weather_main(msg['FromUserName'], city)

itchat.auto_login(hotReload=True)
itchat.run()

def timer(n):
    while True:
        weather_main("要发送的人备注", "城市")  # 此处为要执行的任务
        time.sleep(n)