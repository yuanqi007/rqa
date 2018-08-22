# coding=utf-8

import pandas as pd

index_data = pd.read_excel('D:\\rqadatas\\000001.xlsx',
                           parse_datas=['时间'],
                           date_parser=lambda date: date.split(',')[0])
#index_data['时间'] = index_data['时间'].str.spilt(',', expand=True)[0]

index_data = index_data[['时间','最高','最低','收盘','涨跌']]
index_data.sort_values('时间', inreplace=True)

N1 = 20
N2 = 10

#index_data['最近%s个交易日的最高点' % N1] = index_data['最高'].rolling(N1).max()
#index_data['最近%s个交易日的最高点' % N1].fillna(value=index_data['最近%s个交易日的最高点' % N1].expanding().max(), inplace=True)
# 以上两句，可以用一句话实现
index_data['最近%s个交易日的最高点' % N1] = index_data['最高'].rolling(N1, min_periods=1).max()

index_data['最近%s个交易日的最低点' % N2] = index_data['最低'].rolling(N2, min_periods=1).min()


buy_index = index_data[index_data['收盘'] > index_data['最近%s个交易日的最高点' % N1].shift(1)].index
index_data.loc[buy_index, '收盘时发出的信号'] = 1

sell_index = index_data[index_data['收盘'] < index_data['最近%s个交易日的最低点' % N2].shift(1)].index
index_data.loc[sell_index, '收盘时发出的信号'] = 0

index_data['当天的仓位'] = index_data['收盘时发出的信号'].shift(1)
index_data['当天的仓位'].fillna(method='ffill', inplace=True)



