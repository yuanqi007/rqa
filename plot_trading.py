from __future__ import division

import numpy as np
import pandas as pd
import warnings

warnings.formatwarnings('ignore')

# 计算复权价格
def cal_right_price(input_stock_data, type='前复权'):
    '''

    :param input_stock_data: 标准股票数据，需要收盘价、涨跌幅
    :param type: 前复权、后复权
    :return: 新增一列前复权价格（或后复权价）的stock_data
    '''

    #计算收盘复权价
    stock_data = input_stock_data.copy()
    num = {'后复权': 0, '前复权': -1}
    price1 = stock_data['close'].iloc[num[type]]
    stock_data['复权价_temp'] = (stock_data['change'] + 1.0).cumprod()
    price2 = stock_data['复权价_temp'].iloc[num[type]]
    stock_data['复权价'] = stock_data['复权价_temp'] * (price1 / price2)
    stock_data.pop('复权价_temp')

    #计算开盘复权价
    stock_data['复权价_开盘'] = stock_data['复权价'] / (stock_data['close'] / stock_data['open'])
    return stock_data[['复权价_开盘', '复权价']]


# 获取指定股票对应的数据并按日期升序排序
def get_stock_data(stock_code):
    '''

    :param stock_code: 股票代码
    :return: 返回股票数据集（代码、日期、开盘价、收盘价、涨跌幅）
    '''

    # 此处为存放CSV文件的本地路径，请自行改正地址
    stock_data = pd.read_csv('',parse_dates=['date'])
    stock_data = stock_data[['code', 'date', 'open', 'close', 'change']]
    stock_data.sort_values(by='date', inplace=True)
    stock_data.reset_index(drop=True, inplace=True)

    #计算复权价格
    stock_data[['open', 'close']] = cal_right_price(stock_data, type='后复权')
    return stock_data

# 判断交易天数，如有不满足就不运行程序
def stock_trading_days(stock_data, trading_days=500):
    '''

    :param stock_data: 股票数据集
    :param trading_days: 交易天数下限，默认500天
    :return: 判断股票的交易天数是否大于trading_days，如果不满足就退出程序
    '''

    if len(stock_data) < trading_days:
        print('股票上市时间过短，不运行策略')
        exit(1)

# 简单均线策略，输出每天的仓位
def simple_ma(stock_data, window_short=5, window_long=60):
    '''

    :param stock_data: 股票数据集
    :param window_short: 较短的窗口期
    :param window_long: 较长的窗口期
    :return: 当天收盘时持有该股票的仓位
    '''

    # 计算短期和长期移动平均线
    stock_data['ma_short'] = stock_data['close'].rolling(window_short, min_periods=1).mean()
    stock_data['ma_long'] = stock_data['close'].rolling(window_long, min_periods=1).mean()

    # 出现买入信号且第二天开盘没有涨停
    stock_data.ix[(stock_data['ma_short'].shift(1) > stock_data['ma_long'].shift(1)) &
                  (stock_data['open'] < stock_data['close'].shift(1) * 1.097), 'position'] = 1

    # 出现卖出信号二期第二天开盘没有跌停
    stock_data.ix[(stock_data['ma_short'].shift(1) < stock_data['ma_long'].shift(1)) &
                  (stock_data['open'] > stock_data['close'].shift(1) * 0.903), 'position'] = 0

    stock_data['position'].fillna(method='ffill', inplace=True)
    stock_data['position'].fillna(0, inplace=True)

    return stock_data[['code', 'date', 'open', 'close', 'change', 'position']]


# 根据每日仓位计算总资产的日收益率
def account(df, slippage=1.0/1000, commision_rate=2.5/1000):
    '''

    :param df: 股票账户数据集
    :param slippage: 买卖滑点，默认为1.0/1000
    :param commision_rate: 手续费，默认为2.5/1000
    :return: 返回账户资产的日收益率和日累计收益率的数据字典
    '''

    # 当加仓时，计算当天资金曲线涨幅capital_rtn, capital_rtn=昨天的position在今天涨幅+今天开盘新买入的position在今天的涨幅（扣除手续费）
    df.loc[df['position'] > df['position'].shift(1), 'capital_rtn'] = \
        (df['close'] / df['open'] - 1) * \
        (1 - slippage - commision_rate) * (df['position'] - df['position'].shift(1)) + \
        df['change'] * df['position'].shift(1)
    # 当减仓时，计算当天资金曲线涨幅capital_rtn, capital_rtn=今天开盘卖出的position在今天的涨幅（扣除手续费）+还剩的position在今天的涨幅
    df.loc[stock_data['position'] < df['position'].shift(1), 'capital_rtn'] = \
        (df['open'] / df['close'].shift(1) - 1) * \
        (1 - slippage - commision_rate) * \
        (df['position'].shift(1) - df['position']) + df['change'] * df['position']
    # 当仓位不变时，当天的capital_rtn=当天涨幅*当天的position
    df.loc[df['position'] == df['position'].shift(1), 'capital_rtn'] = df['change'] * df['position']

    df['capital_rtn'].iloc[0] = 0

    return df

# 选取时间段，来计算资金曲线
def select_date_range(stock_data, start_date=pd.to_datetime('20060101'), trade_days=250):
    '''

    :param stock_data:
    :param start_date:
    :param trade_days:
    :return: 对于一个指定的股票，计算回测资金曲线时，从该股票上市交易了trading_days天之后才开始计算，并且最早不早于start_date
    '''

    stock_data = stock_data[trade_days:]
    stock_data = stock_data[stock_data['date'] >= start_date]
    stock_data.reset_index(inplace=True, drop=True)

    return  stock_data

# 计算最近250天的股票，策略累计涨跌幅，以及每年（月、周）股票策略收益
def period_return(stock_data, days=250, if_print=False):
    '''

    :param stock_data: 包含日期、股票涨跌幅和总资产跌幅的数据集
    :param days: 最近250天
    :param if_print: 输出最近250天的股票和策略累计涨跌幅以及每年的股票收益和策略收益
    :return:
    '''

    df = stock_data[['code', 'date', 'change', 'capital_rtn']]

    # 计算每一年（月、周）股票，资金曲线的收益