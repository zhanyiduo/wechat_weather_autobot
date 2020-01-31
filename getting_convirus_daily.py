import time
import json
import requests
from datetime import datetime
import numpy as np
import pandas as pd

def get_distribution():
    """get the regional distribution"""
    province = {}
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=wuwei_ww_area_counts&callback=&_=%d' % int(time.time() * 1000)
    regional_data = json.loads(requests.get(url=url).json()['data'])
    for item in regional_data:
        if item['area'] not in province.keys():
            province.update({item['area']: 0})
        province[item['area']] += int(item['confirm'])
    return province,regional_data

def get_daily_count():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=wuwei_ww_cn_day_counts&callback=&_=%d' % int(time.time() * 1000)
    data = json.loads(requests.get(url=url).json()['data'])
    data.sort(key=lambda x: x['date'])
    df = pd.DataFrame.from_records(data)
    df[['confirm', 'dead', 'heal', 'suspect']] = df[['confirm', 'dead', 'heal', 'suspect']].astype(int)
    return df,data

def virus_stat_text(region=['武汉','辽宁']):

    daily_df,daily_list = get_daily_count()
    today_stat = daily_list[-1]
    province_data,city_data = get_distribution()
    #get national data
    dt = today_stat['date']
    confirm = today_stat['confirm']
    suspect = today_stat['suspect']
    dead = today_stat['dead']
    virus_stat_text_list = [f'{dt}日最新2019-nCOV统计：']
    virus_stat_text_list.append(f'全国确诊{confirm}例，疑似{suspect}例，死亡{dead}例')

    #get city data
    for item in city_data:
        if item['city'] in region:
            city = str(item['city'])
            confirm = str(item['confirm'])
            dead = str(item['dead'])
            virus_stat_text_list.append(f'{city}确诊{confirm}例，死亡{dead}例')
    for i in region:
        if i in province_data.keys():
            confirm = str(province_data[i])
            virus_stat_text_list.append(f'{i}确诊{confirm}例')
    return virus_stat_text_list

if __name__ == '__main__':
    print(virus_stat_text())