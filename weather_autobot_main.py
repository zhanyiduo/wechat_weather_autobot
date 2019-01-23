import itchat
from itchat.content import *
from get_weather_from_api import get_weather_from_api
from apscheduler.schedulers.blocking import BlockingScheduler

with open('api_key.txt', 'r') as f:
    ak = f.readlines()
ak = [x.strip() for x in ak]

def weather_main(userName,theCity='St. Louis',zip=63017,ak=None, scheduled_job = False):
    weather = get_weather_from_api(ak)
    if not scheduled_job:
        if theCity=='zip mode':
            weather_text_list = weather.get_weather_by_zip(zip)
        elif theCity:
            weather_text_list = weather.get_weather_by_city(theCity)
        else:
            return print('No City found')
    else:
        weather_text_list = weather.get_hourly_weather_data_by_zip(weather_data_pnt=5)

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
        weather_main(msg['FromUserName'], city, ak=ak)

@itchat.msg_register([TEXT], isGroupChat=True)
def text_reply(msg):
    if not msg['User']['NickName'] == '咱们这一家子':
        return None
    else:
        city = extract_cityname(msg['Text'])
        if city:
            weather_main(msg['FromUserName'], city, ak=ak)

itchat.auto_login(hotReload=True)
#itchat.run()
#'@b585175d4de9aa775dea56070453ba0c'
def my_cron_job():
    weather_main(userName='@b585175d4de9aa775dea56070453ba0c',ak=ak, scheduled_job=True)
    weather_main(userName='@d9eed6209c06a76b414b503d461c0991234ebe5d3cf13ed1172867b052dec2d8', ak=ak, scheduled_job=True)
    weather_main(userName='@6af565b660f33b488ea576d7800f1b675dc76439e7f49d2a5bd0ee8db0f80917', ak=ak, scheduled_job=True)
    weather_main(userName='@0bab99fc303c55c257712f8b6ba7f0d7dda1e1ef948ea17f2c4d036a8d42157f', ak=ak, scheduled_job=True)
    weather_main(userName='@537c14efa69da4dfc91cd38ff1ffb4c5c40b55c9d898347c6ae72e0f5591e877', ak=ak, scheduled_job=True)
    print('my cron job')

'''Start Scheduling Job'''
sched = BlockingScheduler()
sched.add_job(my_cron_job, 'cron', id='my_cron_job1', hour=7)
#sched.add_job(itchat.run(), 'interval', id='my_job_id', seconds=5)
sched.start()