# coding:utf-8
from wxpy import *
# 导入wxpy模块的全部内容
from apscheduler.schedulers.background import BlockingScheduler
import os
import configparser
from mysql_test import insert_to_sql,update_to_sql,read_from_sql


# 获取文件的当前路径（绝对路径）
cur_path = os.path.dirname(os.path.realpath(__file__))

# 获取config.ini的路径
config_path = os.path.join(cur_path, 'conf.ini')

conf = configparser.ConfigParser()
conf.read(config_path)
hour_set = conf.get('wxpy_test', 'hour')
hour_set = int(hour_set)
QRcode_path = conf.get('wxpy_test', 'pic_path')
print(QRcode_path)


bot=Bot(qr_path=str(QRcode_path))

# 初始化机器人，电脑弹出二维码，用手机微信扫码登陆
bot.groups(update=True, contact_only=False)
my_groups = bot.groups()
# 微信登陆后，更新微信群列表（包括未保存到通讯录的群）
my_group=my_groups.search("为解放威哥而战斗")[0]
my_group.send("everybody，我是杨超越！")
my_friend = bot.friends().search("老张")[0]
# 从群中搜索朋友，但是没有send功能
# my_friend = my_group.search(Member='成威威')
my_friend.send("hello!")

print (my_friend)

my_group.update_group(members_details=True)


# 接收群消息
@bot.register([my_friend, my_group], TEXT, except_self=False)
def print_msg(msg):
    print("msg.chat:", msg.chat)
    print("my_group:", my_group)
    print("msg.is_at:", msg.is_at)
    print("isinstance:", isinstance(msg.chat, Group))
    # 如果是群聊，但没有被 @，则不回复
    if isinstance(msg.chat, Group) and not msg.is_at:
        return
    # 如果是管理员私聊，则执行以下操作
    elif isinstance(msg.chat, Group) is False:
        print(msg.text)
        # 审核跑步记录
        if msg.text.lower() == 'uncheck':
            sql_uncheck = "select d.RECORD_ID, m.USER_NAME, d.RUN_DISTANCE, d.RUN_SPEED, d.DATE_CREATED, d.RECORD_STATUS " \
                          "from runner_detail d inner join runner_target t on d.target_id = t.target_id " \
                          "inner join runner_members m on t.user_id = m.user_id and t.is_last=1 where d.record_status=1;"
            uncheck_re = read_from_sql(sql_uncheck)
            print(uncheck_re)
            uncheck_re.rename(columns={'RECORD_ID': '记录id', 'USER_NAME': '用户', 'RUN_DISTANCE': '距离',
                                       'RUN_SPEED': '配速', 'DATE_CREATED': '记录时间', 'RECORD_STATUS':'审核状态'},
                              inplace=True)
            my_friend.send(uncheck_re)
        elif msg.text.lower().split(' ')[0] == 'pass':
            print(msg.text)
            order = msg.text.split(' ')
            for i in range(1, len(order)):
                sql_check = "update runner_detail d set d.record_status = 2 where d.record_id = "+str(order[i])
                update_to_sql(sql_check)
                print(sql_check)
            my_friend.send("审核了"+str(len(order)-1)+"条记录！")
        else:
            return
    else:
        print(msg.text)
        print (msg.member)
        print (msg.member.name)
        inf = msg.text.split('\u2005')[1:]
        inform = inf[0].split(' ') # inform: ['add', '5', '0530']
        print(inform)
        # 添加跑步记录操作
        if inform[0].lower() == 'add':
            sql1 = "select * from runner_members t where t.user_name = '"+msg.member.name+"'"
            print (sql1)
            uid = read_from_sql(sql1)['USER_ID'][0]
            print(uid)
            print(type(uid))
            sql2 = 'select * from runner_target t where t.is_last = 1 and t.user_id = '+str(uid)
            print(sql2)
            tid = read_from_sql(sql2)['TARGET_ID'][0]
            sql = 'insert into runner_detail (USER_ID,TARGET_ID,RUN_DISTANCE,RUN_SPEED) values ('+str(uid)+','+str(tid)+',' + inform[1]+','+inform[2]+')'
            print (sql)
            insert_to_sql(sql)
            my_group.send("添加成功！")
        # 查看本群本周跑步完成情况
        elif inform[0].lower() == 'vi':
            sql_vi = "select m.USER_NAME, d.RUN_DISTANCE, d.DATE_CREATED from runner_detail d inner join " \
                     "runner_target t on d.target_id = t.target_id inner join " \
                     "runner_members m on t.user_id = m.user_id where t.is_last=1 and d.RECORD_STATUS=2;"
            detail = read_from_sql(sql_vi)
            print(detail)
            detail.rename(columns={'USER_NAME': '用户', 'RUN_DISTANCE': '距离', 'DATE_CREATED': '记录时间'}, inplace = True)
            my_group.send(detail)
        else:
            return


# 堵塞进程，直到结束消息监听 (例如，机器人被登出时)
bot.join()