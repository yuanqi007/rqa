# 策略分析
import pandas as pd
import numpy as np

#获取数据
def get_stock_data(stock_code, index_code, start_date, end_date):

    stock_data = pd.read_excel('D:\\rqadatas\\%s.xlsx' % stock_code, parse_dates=['date'])
    benchmark = pd.read_excel('D:\\rqadatas\\%s.xlsx' % index_code, parse_dates=['date'])

    #生成日期序列
    date = pd.date_range(start_date, end_date)

    #选取日期范围内的股票并排序
    stock_data = stock_data.ix[stock_data['date'].isin(date), ['date', 'change', 'adjust_price']]
    stock_data.sort_values('date', inplace=True)

    date_list = list(start_date['date'])
    benchmark = benchmark.ix[benchmark['date'].isin(date_list), ['date', 'change', 'close']]
    benchmark.sort_values('date', inplace=True)
    benchmark.set_index('date', inplace=True)

    #将回测数据要用的各个序列转换成list格式
    date_line = list(benchmark.index.strftime('%Y-%m-%d')) #日期序列
    capital_line = list(stock_data['adjust_price']) #账户价值序列
    return_line = list(stock_data['change']) #收益率序列
    index_return_line = list(benchmark['change']) #指数的变化率序列
    index_line = list(benchmark['close'])#指数序列

    return date_line, capital_line, return_line, index_line, index_return_line

#计算年化收益率
def annual_return(date_line, captial_line):
    #将数据合并按日期排序
    df = pd.DataFrame({'date': date_line, 'captial': captial_line})
    df.sort_values(by='date', inplace=True)
    df.reset_index(drop=True, inplace=True)

    rng = pd.period_range(start=df['date'].iloc[0], end=df['date'].iloc[-1], freq='D')

    annual = pow(df['captial'].iloc[-1] / df['captial'].iloc[0], 250 / len(rng)) - 1

    return annual

#计算最大回撤函数
def max_drawdown(date_line, captial_line):

    df = pd.DataFrame({'date': date_line, 'captial': captial_line})
    df.sort_values(by='date', inplace=True)
    df.reset_index(drop=True, inplace=True)

    df['max2here'] = df['captial'].expanding().max() #计算当日之前的账户最大市值
    df['dd2here'] =  df['captial'] / df['max2here'] - 1 #计算当日回撤

    #计算回撤最大日期
    temp = df.sort_values(by='dd2here').iloc[0, ['date', 'dd2here']]
    max_dd = temp['dd2here']
    end_date = temp['date']

    #计算开始日期
    df = df[df['date'] <= end_date]
    start_date = df.sort_values(by='captial', ascending=False).iloc[0, 'date']

    print('最大回撤为：%f，开始日期：%s，结束日期：%s' % (max_dd, start_date, end_date))

#计算平均涨幅
def average_change(date_line, return_line):

    df = pd.DataFrame({'date': date_line, 'rtn': return_line})
    avg = df['rtn'].mean()
    print('平均涨幅为：%f' % avg)

#计算上涨概率
def prod_up(date_line, return_line):

    df = pd.DataFrame({'date': date_line, 'rtn': return_line})
    df.loc[df['rtn'] > 0, 'rtn'] = 1
    df.loc[df['rtn'] <= 0, 'rtn'] = 0

    p_up = df['rtn'].sum() / df['rtn'].count()

    print('上涨概率为：%f' % p_up)

#计算最大连续上涨天数和最大连续下跌天数
def max_successive_up(date_line, retrun_line):

    df = pd.DataFrame({'date': date_line, 'rtn': retrun_line})
    s = pd.Series(np.nan, index=df.index)
    s.name = 'up'
    df = pd.concat([df, s], axis=1)
    df.loc[df['rtn'] > 0, 'up'] = 1
    df.loc[df['rtn'] < 0, 'up'] = 0
    df['up'].fillna(method='ffill', inplace=True)

    rtn_list = list(df['up'])
    successive_up_list = []

    for i in range(len(rtn_list)):

        if i == 0:
            num = 1
        else:
            if (rtn_list[i] == rtn_list[i - 1] == 1) or (rtn_list[i] == rtn_list[i - 1] == 0):
                num = num + 1
            else:
                num = 1

        successive_up_list.append(num)

    df['successive_up'] = successive_up_list

    max_successive_up = df.loc[df['up'] == 1, 'successive_up'].sort_values('successive_up', ascending=False).iloc[0]
    max_successive_down = df.loc[df['up'] == 0, 'successive_up'].sort_values('successive_up', ascending=False).iloc[0]

    print('最大连续上涨天数为：%d，最大连续下跌天数为：%d' % (max_successive_up, max_successive_down))
