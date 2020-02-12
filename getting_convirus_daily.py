import time
import json
import requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
# from SIR_prediction import get_predition

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
    #df['infect'] = np.diff(df['confirm'].values, prepend=0, n=1)
    df['month'], df['day'] = df['date'].str.split('/').str
    df['date'] = df.apply(lambda x: datetime.strptime('2020-%s-%s' % (x['month'], x['day']), '%Y-%m-%d'), axis=1)
    df.drop(['month', 'day'], axis=1, inplace=True)
    return df,data

def virus_stat_text(region=['武汉','辽宁']):

    daily_df,daily_list = get_daily_count()
    today_stat = daily_list[-1]
    #province_data,city_data = get_distribution()
    province_data, city_data = [],[]
    #get national data
    dt = today_stat['date']
    confirm = today_stat['confirm']
    suspect = today_stat['suspect']
    dead = today_stat['dead']
    virus_stat_text_list = ['{}日最新2019-nCoV疫情统计：'.format(dt)]
    virus_stat_text_list.append('全国确诊{0}例，疑似{1}例，死亡{2}例'.format(confirm,suspect,dead))

    #get city data
    for item in city_data:
        if item['city'] in region:
            city = str(item['city'])
            confirm = str(item['confirm'])
            dead = str(item['dead'])
            virus_stat_text_list.append('{0}确诊{1}例，死亡{2}例'.format(city,confirm,dead))
    for i in region:
        if province_data:
            if i in province_data.keys():
                confirm = str(province_data[i])
                virus_stat_text_list.append('{0}确诊{1}例'.format(i,confirm))

   # peaknum,peakdate = get_predition(daily_df)
   # virus_stat_text_list.append('预测最终感染人数：{0}\n预测{1}感染人数达到峰值'.format(peaknum,peakdate))
    print(virus_stat_text_list)
    return virus_stat_text_list

if __name__ == '__main__':
    print(virus_stat_text())