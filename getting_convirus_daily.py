import time
import json
import requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.integrate import odeint

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
    df['infect'] = np.diff(df['confirm'].to_numpy(), prepend=0, n=1)
    df['month'], df['day'] = df['date'].str.split('/').str
    df['date'] = df.apply(lambda x: datetime.strptime('2020-%s-%s' % (x['month'], x['day']), '%Y-%m-%d'), axis=1)
    df.drop(['month', 'day'], axis=1, inplace=True)
    return df,data

# growth function
class growth_function():
    def __init__(self, df, N=1e+5):
        # self.df = df.loc[df['suspect']>100,].reset_index(drop=True)
        self.df = df.iloc[-5:, ].reset_index(drop=True)
        self.N = N
        self.t = self.df.index.astype(int).to_numpy()
        self.I = self.df['confirm'].to_numpy()
        self.R = self.df['heal'].to_numpy()
        self.S = self.N - self.I - self.R
        self.xi = [self.get_xi(t) for t in self.t]
        self.beta = self.fit_beta()
        self.gamma = self.fit_gamma()

    def get_xi(self, t):
        return sum(self.I[:t + 1])  # xi = sum(I)

    def s_func(self, t, beta):
        S0 = self.S[0]
        return [S0 * np.exp(-beta * self.xi[i] / self.N) for i in t]  # S = S0*exp(-beta*xi[t]/N)

    def r_func(self, t, gamma):
        R0 = self.R[0]
        return [R0 + gamma * self.xi[i] for i in t]  # R = R0 + gamma*xi[t]

    def i_func(self, t, S, R):
        return [self.N - S[i] - R[i] for i in t]

    def fit_beta(self):
        xdata = self.t
        ydata = self.S
        popt, pcov = curve_fit(self.s_func, xdata, ydata)
        print('Beta = ' + str(popt[0]))
        return popt[0]

    def fit_gamma(self):
        xdata = self.t
        ydata = self.R
        popt, pcov = curve_fit(self.r_func, xdata, ydata)
        print('Gamma = ' + str(popt[0]))
        return popt[0]

    def deriv(self, y, t, N, beta, gamma):
        S, I, R = y
        dSdt = -beta * S * I / N
        dIdt = beta * S * I / N - gamma * I
        dRdt = gamma * I
        return dSdt, dIdt, dRdt

    def predict(self, t):
        # Initial conditions vector
        y0 = self.S[0], self.I[0], self.R[0]
        # Integrate the SIR equations over the time grid, t.
        ret = odeint(self.deriv, y0, t, args=(self.N, self.beta, self.gamma))
        S, I, R = ret.T
        return S, I, R

def get_predition(df):
    model = growth_function(df, N=1e+6)
    predx = np.arange(model.df.index.to_numpy()[-1] + 100)
    predS, predI, predR = model.predict(predx)
    preddate = [min(model.df['date']) + timedelta(days=int(x)) for x in predx]
    predy = list(predI)
    peak_num = int(max(predy))
    peak_date = preddate[predy.index(max(predy))].strftime("%m-%d")
    return peak_num,peak_date

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

    peaknum,peakdate = get_predition(daily_df)
    virus_stat_text_list.append('预测最终感染人数：{0}\n预测{1}感染人数达到峰值'.format(peaknum,peakdate))
    print(virus_stat_text_list)
    return virus_stat_text_list

if __name__ == '__main__':
    print(virus_stat_text())