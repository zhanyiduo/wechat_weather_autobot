import requests
import json
import re
import pandas as pd
import datetime

class get_weather_from_api(object):
    def __init__(self,ak=None):
        assert ak, "api access key is empty!"
        self.ak = ak #get the api access key
        return None

    def get_weather_by_city(self,cityname='None'):
        ak_baidu = self.ak[0]
        ak_weather = self.ak[1]
        '''If there is chinese character in the cityname, then use baidu weather api'''
        weather_text_list = []
        if re.search(u'[\u4e00-\u9fff]', cityname):
            # url = 'http://api.map.baidu.com/telematics/v3/weather?location={city}&output=json&ak=TueGDhCvwI6fOrQnLM0qmXxY9N0OkOiQ&callback=?' \
            url = 'http://api.map.baidu.com/telematics/v3/weather?location={city}&output=json&ak={ak}&callback=?' \
                .format(city=cityname, ak=ak_baidu)
            # 使用requests发起请求，接受返回的结果
            rs = requests.get(url)
            # 使用loads函数，将json字符串转换为python的字典或列表
            rs_dict = json.loads(rs.text)
            if rs_dict['status'] == 'success':
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
                weather_text_list.append(city_name + '地区天气预报：')
                for weather_dict in weather_data:
                    # 取出日期，天气，风级，温度
                    date = weather_dict['date']
                    weather = weather_dict['weather']
                    wind = weather_dict['wind']
                    temperature = weather_dict['temperature']
                    weather_text_list.append(date + weather + wind + temperature)
        else:
            url = 'http://api.openweathermap.org/data/2.5/forecast?' \
                  'q={city},{country}&mode=json&units=metric&APPID={APIKEY}' \
                .format(city=cityname, country='US', APIKEY=ak_weather)
            rs = requests.get(url)
            rs_dict = json.loads(rs.text)
            error_code = rs_dict['cod']
            if int(error_code) == 200:
                weather_text_list = self.extract_weather_data(rs_dict)
        return weather_text_list
    def get_weather_by_zip(self,zipcode=63017):
        ak_weather = self.ak[1]
        weather_text_list = []
        url = 'http://api.openweathermap.org/data/2.5/forecast?' \
              'zip={zip_code},{country}&mode=json&units=metric&APPID={APIKEY}' \
            .format(zip_code=zipcode, country='US', APIKEY=ak_weather)
        rs = requests.get(url)
        rs_dict = json.loads(rs.text)
        error_code = rs_dict['cod']
        if int(error_code) == 200:
            weather_text_list = self.extract_weather_data(rs_dict)

        return weather_text_list
    def get_hourly_weather_data_by_zip(self, zipcode=63017, weather_data_pnt=7):
        ak_weather = self.ak[1]
        weather_text_list = []
        url = 'http://api.openweathermap.org/data/2.5/forecast?' \
              'zip={zip_code},{country}&mode=json&units=metric&APPID={APIKEY}&cnt={cnt}' \
            .format(zip_code=zipcode, country='US', APIKEY=ak_weather, cnt=weather_data_pnt)
        rs = requests.get(url)
        rs_dict = json.loads(rs.text)
        error_code = rs_dict['cod']
        if int(error_code) == 200:
            weather_data = rs_dict['list']
            city_name = rs_dict['city']['name']
            weather_text_list.append(city_name + '地区天气预报：')
            print('City:' + city_name)
            weather_hourly_list = []
            for weather_dict in weather_data:
                _date_ = pd.to_datetime(weather_dict['dt_txt']).date()
                weekday = pd.to_datetime(weather_dict['dt_txt']).weekday()
                date_time = weather_dict['dt_txt']
                time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').time()
                weather = weather_dict['weather'][0]['description']
                temp_min = float(weather_dict['main']['temp_min'])
                temp_max = float(weather_dict['main']['temp_max'])
                temp = float(weather_dict['main']['temp'])
                wind = float(weather_dict['wind']['speed'])
                weather_hourly_list.append([time, weekday, weather, temp, wind])
            weather_hourly_df = pd.DataFrame(weather_hourly_list,
                                             columns=['time', 'weekday', 'weather', 'temp', 'wind'])
            weather_hourly_df['hour'] = weather_hourly_df['time'].astype(str).str.split(':', expand=True).get(0)
            weather_hourly_df['weather'] = weather_hourly_df['weather'].apply(lambda x: list(set(x.lower().split(','))))
            weather_hourly_df['weekday_chn'] = weather_hourly_df['weekday'].apply(
                lambda x: self.convert_weekday_to_chinese(x))
            # append time to weekday
            weather_hourly_df['weekday_chn'] = weather_hourly_df['weekday_chn'] + weather_hourly_df['hour'] + "时"
            weather_hourly_df['weather_chn'] = weather_hourly_df['weather'].apply(
                lambda x: self.convert_weather_to_chinese(x))
            weather_hourly_df['temp_chn'] \
                = weather_hourly_df.apply(lambda row: '，气温' + str(int(row['temp'])) + '℃', axis=1)
            weather_hourly_df['wind_chn'] = weather_hourly_df['wind'].apply(
                lambda x: '，风速' + str(round(3.6 * x, 1)) + 'km/h')

            weather_hourly_df.apply(lambda row: weather_text_list.append(row['weekday_chn'] +
                                                                         row['weather_chn'] +
                                                                         row['temp_chn'] +
                                                                         row['wind_chn']),
                                    axis=1)
        return weather_text_list
    def extract_weather_data(self, rs_dict):
        weather_text_list = []
        weather_data = rs_dict['list']
        city_name = rs_dict['city']['name']
        weather_text_list.append(city_name + '地区天气预报：')
        print('City:' + city_name)
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
        weather_daily_df = weather_hourly_df.groupby(by=['weekday'], sort=False).agg({'temp_min': 'min',
                                                                                      'temp_max': 'max',
                                                                                      'wind': 'mean',
                                                                                      'weather': lambda
                                                                                          x: "%s" % ','.join(x)})
        weather_daily_df = weather_daily_df.reset_index()
        weather_daily_df['weather'] = weather_daily_df['weather'].apply(lambda x: list(set(x.lower().split(','))))
        weather_daily_df['weekday_chn'] = weather_daily_df['weekday'].apply(
            lambda x: self.convert_weekday_to_chinese(x))
        weather_daily_df['weather_chn'] = weather_daily_df['weather'].apply(
            lambda x: self.convert_weather_to_chinese(x))
        weather_daily_df['temp_chn'] \
            = weather_daily_df.apply(lambda row: '，气温' + str(int(row['temp_min'])) + '~'
                                                 + str(int(row['temp_max'])) + '℃', axis=1)
        weather_daily_df['wind_chn'] = weather_daily_df['wind'].apply(lambda x: '，风速' + str(round(3.6 * x, 1)) + 'km/h')

        weather_daily_df.apply(lambda row: weather_text_list.append(row['weekday_chn'] +
                                                                    row['weather_chn'] +
                                                                    row['temp_chn'] +
                                                                    row['wind_chn']),
                               axis=1)
        return weather_text_list
    @staticmethod
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
            elif 'snow' in txt:
                if '雪' in weather_chn:
                    continue
                else:
                    weather_chn = weather_chn + '雪'
            if txt != text_set[-1]:
                weather_chn = weather_chn + '转'
        if weather_chn.endswith('转'):
            weather_chn = weather_chn[:-1]
        return weather_chn
    @staticmethod
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



if __name__ == "__main__":
    with open('api_key.txt', 'r') as f:
        ak = f.readlines()
    ak = [x.strip() for x in ak]
    weather = get_weather_from_api(ak)
    print(weather.get_hourly_weather_data_by_zip())
    print(weather.get_weather_by_zip())
    print(weather.get_weather_by_city('New York'))
    print(weather.get_weather_by_city('武汉'))