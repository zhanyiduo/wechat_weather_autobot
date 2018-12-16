import requests
import json
import itchat
import re
import pandas as pd

def extract_weather_data(rs_dict):
    weather_text_list=[]
    weather_data = rs_dict['list']
    city_name = rs_dict['city']['name']
    weather_text_list.append(city_name+'地区天气预报：')
    print('City:'+city_name)
    weather_hourly_list = []
    for weather_dict in weather_data:
        _date_ = pd.to_datetime(weather_dict['dt_txt']).date()
        weekday = pd.to_datetime(weather_dict['dt_txt']).weekday()
        date_time = weather_dict['dt_txt']
        weather = weather_dict['weather'][0]['description']
        temp_min = float(weather_dict['main']['temp_min'])
        temp_max = float(weather_dict['main']['temp_max'])
        wind = float(weather_dict['wind']['speed'])
        weather_hourly_list.append([_date_, weekday, weather, temp_min, temp_max, wind])
    weather_hourly_df = pd.DataFrame(weather_hourly_list,
                                     columns=['date', 'weekday', 'weather', 'temp_min', 'temp_max', 'wind'])
    '''convert hourly weather to daily'''
    weather_daily_df = weather_hourly_df.groupby(by=['weekday'],sort=False).agg({'temp_min': 'min',
                                                                      'temp_max': 'max',
                                                                      'wind': 'mean',
                                                                      'weather': lambda x: "%s" % ','.join(x)})
    weather_daily_df = weather_daily_df.reset_index()
    weather_daily_df['weather'] = weather_daily_df['weather'].apply(lambda x: list(set(x.lower().split(','))))

    def convert_weekday_to_chinese(weekday):
        weekday = int(weekday)
        week_chn = '周'
        if weekday == 6:
            weekday_chn = week_chn + '日'
        elif weekday == 0:
            weekday_chn = week_chn + '一'
        elif weekday == 1:
            weekday_chn = week_chn + '二'
        elif weekday == 2:
            weekday_chn = week_chn + '三'
        elif weekday == 3:
            weekday_chn = week_chn + '四'
        elif weekday == 4:
            weekday_chn = week_chn + '五'
        elif weekday == 5:
            weekday_chn = week_chn + '六'
        return weekday_chn

    weather_daily_df['weekday_chn'] = weather_daily_df['weekday'].apply(lambda x: convert_weekday_to_chinese(x))

    def convert_weather_to_chinese(text_set):
        weather_chn = '天气：'
        for txt in text_set:
            if 'clear' in txt:
                if '晴' in weather_chn:
                    continue
                else:
                    weather_chn = weather_chn + '晴'
            elif 'cloud' in txt:
                if '多云' in weather_chn:
                    continue
                else:
                    weather_chn = weather_chn + '多云'
            elif 'wind' in txt:
                if '风' in weather_chn:
                    continue
                else:
                    weather_chn = weather_chn + '风'
            elif 'rain' in txt:
                if '雨' in weather_chn:
                    continue
                else:
                    weather_chn = weather_chn + '雨'
            if txt != text_set[-1]:
                weather_chn = weather_chn + '转'
        return weather_chn

    weather_daily_df['weather_chn'] = weather_daily_df['weather'].apply(lambda x: convert_weather_to_chinese(x))
    weather_daily_df['temp_chn'] \
        = weather_daily_df.apply(lambda row: '，气温' + str(int(row['temp_min'])) + '~'
                                             + str(int(row['temp_max'])) + '℃', axis=1)
    weather_daily_df['wind_chn'] = weather_daily_df['wind'].apply(lambda x: '，风速' + str(round(x, 1)) + 'm/s')

    weather_daily_df.apply(lambda row: weather_text_list.append(row['weekday_chn'] +
                                                                row['weather_chn'] +
                                                                row['temp_chn'] +
                                                                row['wind_chn']),
                           axis=1)
    return weather_text_list
def get_weather_by_city(cityname='None'):
    '''If there is chinese character in the cityname, then use baidu weather api'''
    weather_text_list = []
    if re.search(u'[\u4e00-\u9fff]', cityname):
        url = 'http://api.map.baidu.com/telematics/v3/weather?location={city}&output=json&ak=TueGDhCvwI6fOrQnLM0qmXxY9N0OkOiQ&callback=?'\
            .format(city=cityname)
        # 使用requests发起请求，接受返回的结果
        rs = requests.get(url)
        # 使用loads函数，将json字符串转换为python的字典或列表
        rs_dict = json.loads(rs.text)
        # 取出error
        error_code = rs_dict['error']
        # 如果取出的error为0，表示数据正常，否则没有查询到结果
        if error_code == 0:
            # 从字典中取出数据
            results = rs_dict['results']
            # 根据索引取出天气信息字典
            info_dict = results[0]
            # 根据字典的key，取出城市名称
            city_name = info_dict['currentCity']
            # 取出pm值
            pm25 = info_dict['pm25']
            # 取出天气信息列表
            weather_data = info_dict['weather_data']
            weather_text_list.append(city_name+'地区天气预报：')
            for weather_dict in weather_data:
                # 取出日期，天气，风级，温度
                date = weather_dict['date']
                weather = weather_dict['weather']
                wind = weather_dict['wind']
                temperature = weather_dict['temperature']
                weather_text_list.append(date+weather+wind+temperature)
    else:
        url = 'http://api.openweathermap.org/data/2.5/forecast?' \
              'q={city},{country}&mode=json&units=metric&APPID={APIKEY}'\
            .format(city=cityname,country='US',APIKEY='340da4ca81cfd1cba05fc94a60cd6293')
        rs = requests.get(url)
        rs_dict = json.loads(rs.text)
        error_code = rs_dict['cod']
        if int(error_code) == 200:
            weather_text_list = extract_weather_data(rs_dict)
    return weather_text_list
def get_weather_by_zip(zipcode = 63017):
    zipcode = 63017
    weather_text_list=[]
    url = 'http://api.openweathermap.org/data/2.5/forecast?' \
          'zip={zip_code},{country}&mode=json&units=metric&APPID={APIKEY}' \
        .format(zip_code=zipcode, country='US', APIKEY='340da4ca81cfd1cba05fc94a60cd6293')
    rs = requests.get(url)
    rs_dict = json.loads(rs.text)
    error_code = rs_dict['cod']
    if int(error_code) == 200:
        weather_text_list = extract_weather_data(rs_dict)

    return weather_text_list
