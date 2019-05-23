# coding:utf-8
import pymysql
import pandas as pd
import datetime


# # 打开数据库连接
# db = pymysql.connect("www.vvcheng.com", "ycy", "paic1234", "runnerdb")
#
# # 使用 cursor() 方法创建一个游标对象 cursor
# cursor = db.cursor()


def insert_to_sql(sql):
    """
    插入数据
    :param cur: 一个游标对象
    :param sql: 要执行的sql语句
    :return:
    """
    # 打开数据库连接
    db = pymysql.connect("www.vvcheng.com", "ycy", "paic1234", "runnerdb")

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    try:
        cursor.execute(sql)
        db.commit()
        print("insert to mysql done!")
        return
    except Exception as e:
        # 回滚
        db.rollback()
    cursor.close()


def update_to_sql(sql):
    """
    更新数据
    :param sql:
    :return:
    """

    # 打开数据库连接
    db = pymysql.connect("www.vvcheng.com", "ycy", "paic1234", "runnerdb")

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 若执行成功，返回1，失败，返回0
    r = '1'
    try:
        cursor.execute(sql)
        db.commit()
        print("update to mysql done!")
        return
    except Exception as e:
        # 回滚
        db.rollback()
        r = '0'
    cursor.close()
    return r


def read_from_sql(sql):
    # 打开数据库连接
    db = pymysql.connect("www.vvcheng.com", "ycy", "paic1234", "runnerdb")

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()  # 获取查询结果
    col_result = cursor.description  # 获取查询结果的字段描述

    columns = []
    for i in range(len(col_result)):
        columns.append(col_result[i][0])  # 获取字段名，咦列表形式保存

    df = pd.DataFrame(columns=columns)
    for i in range(len(result)):
        df.loc[i] = list(result[i])
    cursor.close()
    return df


def this_mon():
    monday = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    while monday.weekday() != 0:
        monday -= one_day
    mon = monday.strftime("%Y%m%d")
    return mon
#
# # 打开数据库连接
# db = pymysql.connect("www.vvcheng.com","ycy","paic1234","runnerdb" )
#
# # 使用 cursor() 方法创建一个游标对象 cursor
# cursor = db.cursor()
#
# # 使用 execute()  方法执行 SQL 查询
# cursor.execute("SELECT * from runner_detail")
#
# # 使用 fetchone() 方法获取单条数据.
# data = cursor.fetchall()
# print(data)
# # print ("Database version : %s " % data)
#
# # 关闭数据库连接
# db.close()


# 将df输出为规范化格式
def strout(df):
    pass