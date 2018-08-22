# coding=utf-8

import pandas as pd
import matplotlib.pyplot as plt
import dbconn

def automatic_investmemt_plan(index_code, start_date, end_date):

    conn = dbconn.get_dbconn()
    index_data = pd.read_sql('select * from tb_k_data where code = %s' % index_code,
                             con=conn,
                             index_col=['tradedate'] ,
                             parse_dates = ['tradedate'])


    index_data = index_data[['code','close']].sort_index()
    index_data = index_data[start_date:end_date]
    index_data['无风险利率'] = (4.0 / 100 + 1) ** (1.0 / 250) - 1
    index_data['无风险利率_净值'] = (index_data['无风险利率'] + 1).cumprod()

    by_month = index_data.resample('M', kind='period').first()

    trade_log = pd.DataFrame(index=by_month.index)
    trade_log['基金净值'] = by_month['close'] / 1000
    trade_log['money'] = 5000.0
    trade_log['基金份额'] = trade_log['money'] / trade_log['基金净值']
    trade_log['总基金份额'] = trade_log['基金份额'].cumsum()
    trade_log['总投入'] = trade_log['money'].cumsum()

    trade_log['理财份额'] = trade_log['money'] / by_month['无风险利率_净值']
    trade_log['总理财份额'] = trade_log['理财份额'].cumsum()

    temp = trade_log.resample('D').ffill()
    index_data = index_data.to_period('D')

    daily_data = pd.concat([index_data, temp[['总基金份额', '总理财份额', '总投入']]], axis=1, join='inner')
    daily_data['基金定投投资金曲线'] = daily_data['close'] / 1000 * daily_data['总基金份额']
    daily_data['理财定投投资金曲线'] = daily_data['无风险利率_净值'] * daily_data['总理财份额']

    return daily_data


def main():
    df = automatic_investmemt_plan('000001','2012-01-01','2015-04-30')
    print(df[['总投入', '基金定投投资金曲线', '理财定投投资金曲线']].iloc[[0, -1], ])

    temp = (df['基金定投投资金曲线'] / df['理财定投投资金曲线'] - 1).sort_values()
    print('最差时基金定投相比理财定投亏损：%.2f%%，日期为：%s' % (temp.iloc[0] * 100,str(temp.index[0])))
    print('最好时基金定投相比理财定投亏损：%.2f%%，日期为：%s' % (temp.iloc[-1] * 100, str(temp.index[-1])))

    df[['基金定投投资金曲线', '理财定投投资金曲线']].plot(figsize=(12,6))
    df['close'].plot(secondary_y=True)

    plt.legend(['close'], loc='best')
    plt.show()


main()




