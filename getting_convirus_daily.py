import time
import json
import requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
# from SIR_prediction import get_predition

def get_china_daily_count():
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

def get_us_daily_count():
    data = {}
    data['national'] = requests.get(url='https://covidtracking.com/api/us').json()
    data['state'] = pd.DataFrame(requests.get(url='https://covidtracking.com/api/states').json())
    return data

def virus_stat_text(state='MO',county ='st.louis'):
    daily_dict = get_us_daily_count()
    today_stat = daily_dict.get('national')[-1]
    confirm = today_stat['positive']
    death = today_stat['death']
    virus_stat_text_list = []
    virus_stat_text_list.append('美国确诊{0}例，死亡{1}例'.format(confirm,death))

    state_df = daily_dict.get('state')
    state_confirm = state_df.loc[state_df['state']==state,'positive'].astype(int).values[0]
    state_death = state_df.loc[state_df['state']==state,'death'].astype(int).values[0]
    virus_stat_text_list.append('密苏里州确诊{0}例，死亡{1}例'.format(state_confirm, state_death))
    print(virus_stat_text_list)
    return virus_stat_text_list

if __name__ == '__main__':
    print(virus_stat_text())