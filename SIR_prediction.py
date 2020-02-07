import numpy as np
from datetime import timedelta
from scipy.optimize import curve_fit
from scipy.integrate import odeint

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