import dbconn

def get_k_datas(code):

    tradedatas = []
    conn = dbconn.get_dbconn()
    sql = 'select * from tb_k_data where code = %s'
    cursor = conn.cursor()
    cursor.execute(sql,(code,))
    datas = cursor.fetchall()
    cursor.close()
    conn.close()

    lastmonth = 0
    for data in datas:
        month = data[2].month

        if lastmonth == month:
            continue
        else:
            tradedatas.append({'code': data[0], 'type': data[1], 'tradedate': data[2], 'open': data[5], 'close': data[8]})
            lastmonth = month

    return tradedatas

def trade(tradedatas):

    totalmoney = 0

    for data in tradedatas:
        Volume = 5000 / data['open']

    pass

def main():
    td = get_k_datas('510500')
    print(len(td))

main()

