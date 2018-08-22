import pymysql

def get_dbconn():

    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        passwd='mysql',
        db='rqa',
        port=3306,
        charset='utf8'
    )
    return conn