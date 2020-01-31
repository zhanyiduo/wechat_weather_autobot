import itchat
from itchat.content import *
from get_weather_from_api import get_weather_from_api
from getting_convirus_daily import virus_stat_text

with open('api_key.txt', 'r') as f:
    ak = f.readlines()
ak = [x.strip() for x in ak]

def send_nCov(userName, region=['武汉','辽宁']):
    virus_stat_text_list = virus_stat_text(region=region)
    for virus_text in virus_stat_text_list:
        itchat.send(virus_text, toUserName=userName)
    return None

def weather_main(userName,theCity='St. Louis',zip=63017,ak=None, scheduled_job = False):
    print(userName)
    weather = get_weather_from_api(ak)
    if not scheduled_job:
        if theCity=='zip mode':
            weather_text_list = weather.get_weather_by_zip(zip)
        elif theCity:
            weather_text_list = weather.get_weather_by_city(theCity)
        else:
            return print('No City found')
    else:
        weather_text_list = weather.get_hourly_weather_data_by_zip(weather_data_pnt=7)

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

def get_username(name=None):
    if itchat.search_friends(name=name)[0]['UserName']:
        return itchat.search_friends(name=name)[0]['UserName']
    else:
        return None

def get_chatroom(name=None):
    if itchat.search_chatrooms(name=name)[0]['UserName']:
        return itchat.search_chatrooms(name=name)[0]['UserName']
    else:
        return None
# 如果对方发的是文字，则我们给对方回复以下的东西
@itchat.msg_register([TEXT])
def text_reply(msg):
    city = extract_cityname(msg['Text'])
    if city:
        weather_main(msg['FromUserName'], city, ak=ak)

@itchat.msg_register([TEXT], isGroupChat=True)
def text_reply(msg):
    if not msg['User']['NickName'] == '咱们这一家子':
        return None
    else:
        city = extract_cityname(msg['Text'])
        if city:
            weather_main(msg['FromUserName'], city, ak=ak)
        send_nCov(userName=get_chatroom('咱们这一家子'))
itchat.auto_login(hotReload=True)
itchat.run()
