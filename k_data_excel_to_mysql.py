import xlrd
import dbconn

from datetime import datetime
from xlrd import xldate_as_tuple


def read_file(filename, code, type):

    #info = {}
    datas = []
    info = ()

    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_name(code)

    for i in range(1, sheet.nrows):
        datevalue = sheet.cell(i, 0).value.split(',')
        '''
        info['code'] = code
        info['tradedate'] = datevalue[0]
        info['week'] = datevalue[1]
        info['klevel'] = 'd'
        info['open'] = sheet.cell(i,1).value
        info['high'] = sheet.cell(i,2).value
        info['low'] = sheet.cell(i,3).value
        info['close'] = sheet.cell(i,4).value
        info['hal'] = sheet.cell(i,5).value
        info['aoi'] = sheet.cell(i,6).value
        info['swing'] = sheet.cell(i,7).value
        info['th'] = sheet.cell(i,8).value / 10000
        info['volume'] = sheet.cell(i,8).value / 100000000
        
        datas.append(info)
        '''
        if type == 'ETF':
            info = (code,
                    type,
                    datevalue[0],
                    datevalue[1],
                    'd',
                    sheet.cell(i, 1).value,
                    sheet.cell(i, 2).value,
                    sheet.cell(i, 3).value,
                    sheet.cell(i, 4).value,
                    0,
                    sheet.cell(i, 5).value,
                    sheet.cell(i, 6).value,
                    sheet.cell(i, 7).value / 10000,
                    sheet.cell(i, 8).value / 100000000,
                    sheet.cell(i, 9).value,
                    sheet.cell(i, 10).value)
        elif type == 'INDEX':
            info = (code,
                    type,
                    datevalue[0],
                    datevalue[1],
                    'd',
                    sheet.cell(i, 1).value,
                    sheet.cell(i, 2).value,
                    sheet.cell(i, 3).value,
                    sheet.cell(i, 4).value,
                    sheet.cell(i, 5).value,
                    sheet.cell(i, 6).value,
                    sheet.cell(i, 7).value,
                    sheet.cell(i, 8).value / 10000,
                    sheet.cell(i, 9).value / 100000000,
                    0,
                    0)

        datas.append(info)

    return datas


def get_sql():
    sql = 'replace into tb_k_data values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    return sql

def save_data_to_db(conn, sql, datas):
    cur = conn.cursor()
    cur.executemany(sql, datas)
    cur.close()
    conn.commit()
    conn.close()


def main():

    fileName = r'd:\\rqadatas\\000001.xlsx'
    code_index = ['000001', '000016', '000905',
                  '399001', '399006', '399300', '399673']
    code_etf = ['159915', '159949', '510050', '510300', '510500']

    '''
    for code in code_index: 
        fileName = 'd:\\rqadatas\\%s.xlsx' % code 
        datas = read_file(fileName, code, 'INDEX')
        sql = get_sql()
        conn = get_dbconn()
        save_data_to_db(conn, sql, datas)
    '''
    for code in code_etf:
        fileName = 'd:\\rqadatas\\%s.xlsx' % code
        datas = read_file(fileName, code, 'ETF')
        sql = get_sql()
        conn = dbconn.get_dbconn()
        save_data_to_db(conn, sql, datas)


main()
