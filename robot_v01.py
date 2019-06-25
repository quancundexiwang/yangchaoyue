# coding:utf-8
from wxpy import *
# 导入wxpy模块的全部内容
from apscheduler.schedulers.background import BackgroundScheduler
import os
import configparser
from mysql_test import insert_to_sql,update_to_sql,read_from_sql,this_mon


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
my_group=my_groups.search("燃烧我的卡路里")[0]
my_group.send("everybody，我是杨超越！")
my_friend = bot.friends().search("杨超越呵呵")[0]
# for i in range(len(my_friend)):
#     print (my_friend[i].nick_name)
# 从群中搜索朋友，但是没有send功能
# my_friend = my_group.search(Member='成威威')
my_friend.send("hello!")

print (my_friend)

my_group.update_group(members_details=True)


def check_str(inform):
    # 检查输入的参数的格式
    # 0 代表输入的数字，1 代表输入的不是数字
    isdigit = '0'
    for f in range(1, len(inform)):
        try:
            f = float(inform[f])
        except ValueError:
            isdigit = '1'
            break
    return isdigit


# 定时任务---心跳
def job_send():
    my_friend.send("i am still running! wow!")


# 定时任务---每周一早上更新跑步目标表
def target_ini():
    # 将上周情况发群里
    my_group.send("上周跑步完成情况如下：")
    sql_vi = "select m.USER_NAME, t.DISTANCE_TARGET, t.DISTANCE_ACTUALLY, t.RUN_WEEK from runner_target t  " \
             "inner join runner_members m on t.user_id = m.user_id where t.is_last=1 and m.RUN_STATUS = 1;"
    detail = read_from_sql(sql_vi)
    detail['DISTANCE_ACTUALLY'] = [round(x, 2) for x in detail['DISTANCE_ACTUALLY']]
    print(detail)
    detail.rename(columns={'USER_NAME': '用户', 'DISTANCE_TARGET': '目标距离','DISTANCE_ACTUALLY':'实际距离', 'RUN_WEEK': '跑步周'}, inplace=True)

    # 上周观众席名单
    sql_viewer = "select m.USER_NAME from runner_members m where m.RUN_STATUS = 2"
    viewer = read_from_sql(sql_viewer)
    m = ''
    for i in range(len(viewer)):
        m = m + str(viewer['USER_NAME'][i])+','

    if viewer.empty:
        my_group.send(detail)
        my_group.send("上周全员参与跑步！")
    else:
        my_group.send(detail)
        my_group.send("上周免跑名单为:" + m)

    # 在新的一周将所有成员改为跑步状态，除开状态为3的成员!
    sql_us = "update runner_members m set m.RUN_STATUS = 1 where m.RUN_STATUS = 2;"
    update_to_sql(sql_us)

    # 将目标表的是否为当前周字段改为0
    sql_uptar = "update runner_target t set t.IS_LAST = 0"
    update_to_sql(sql_uptar)
    sql_uid = "select * from runner_members"
    user = read_from_sql(sql_uid)['USER_ID']
    mon = this_mon()

    for i in range(len(user)):
        sql_int = "insert into runner_target (USER_ID,RUN_WEEK,DISTANCE_TARGET,DISTANCE_ACTUALLY,IS_LAST) " \
                  "values ("+str(user[i])+","+str(mon)+",5,0,1);"
        print(sql_int)
        insert_to_sql(sql_int)


# 定时任务---每天下午6点，给管理员发未审核提示，给群里发本周完成情况。
def check_remind():
    # 给管理员发还有几条记录未审核。
    sql_uncheck = "select * from runner_detail d where d.RECORD_STATUS=1;"
    count_uncheck = read_from_sql(sql_uncheck)
    my_friend.send(str(len(count_uncheck))+"条记录未审核，请审核！")


def comp_information():
    # 本周观众席名单
    sql_viewer = "select m.USER_NAME from runner_members m where m.RUN_STATUS = 2"
    viewer = read_from_sql(sql_viewer)
    m = ''
    for i in range(len(viewer)):
        m = m + str(viewer['USER_NAME'][i]) + ','
    if len(viewer) == 0:
        pass
    else:
        my_group.send("本周免跑名单为:" + m)

    # 将本周已完成情况发群里
    sql_vi = "select m.USER_NAME, t.DISTANCE_TARGET, t.DISTANCE_ACTUALLY, t.RUN_WEEK from runner_target t  " \
             "inner join runner_members m on t.user_id = m.user_id where t.is_last=1 and m.RUN_STATUS = 1;"
    detail = read_from_sql(sql_vi)
    detail['DISTANCE_ACTUALLY'] = [round(x, 2) for x in detail['DISTANCE_ACTUALLY']]
    print(detail)
    detail.rename(
        columns={'USER_NAME': '用户', 'DISTANCE_TARGET': '目标距离', 'DISTANCE_ACTUALLY': '实际距离', 'RUN_WEEK': '跑步周'},
        inplace=True)
    if detail.empty:
        my_group.send("到现在还没人跑呀！快去跑步啦！")
    else:
        my_group.send("本周跑步完成情况如下：")
        my_group.send(detail)


scheduler = BackgroundScheduler()
scheduler.add_job(job_send, "cron", hour="*",  minute=0)
scheduler.add_job(target_ini, "cron", day_of_week='mon', hour=0, minute=0)
scheduler.add_job(check_remind, "cron", hour="12,21",  minute=0)
scheduler.add_job(comp_information, "cron", hour="18",  minute=0)
try:
    scheduler.start()
except SystemExit:
    print('exit')
    exit()
print("lalallalalallallalallal!")


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
        # 审核跑步记录 查看本周记录
        if msg.text.lower() == 're':
            sql_uncheck = "select d.RECORD_ID, m.USER_NAME, d.RUN_DISTANCE, d.RUN_SPEED," \
                          "date_format(d.DATE_CREATED,'%m-%d %H:%i') as DATE_CREATED , d.RECORD_STATUS " \
                          "from runner_detail d inner join runner_target t on d.target_id = t.target_id " \
                          "inner join runner_members m on t.user_id = m.user_id and t.is_last=1 ;"
            uncheck_re = read_from_sql(sql_uncheck)
            uncheck_re['RUN_DISTANCE'] = [round(x, 2) for x in uncheck_re['RUN_DISTANCE']]
            uncheck_re['RUN_SPEED'].fillna('---', inplace=True)
            print(uncheck_re)
            uncheck_re.rename(columns={'RECORD_ID': '记录id', 'USER_NAME': '用户', 'RUN_DISTANCE': '距离',
                                       'RUN_SPEED': '配速', 'DATE_CREATED': '记录时间', 'RECORD_STATUS':'审核状态'},
                              inplace=True)
            if uncheck_re.empty:
                my_friend.send("没有未审核记录哦！")
            else:
                my_friend.send(uncheck_re)

        # 管理员审核通过跑步记录
        elif msg.text.lower().split(' ')[0] == 'pass':
            print(msg.text)
            order = msg.text.split(' ')
            for i in range(1, len(order)):
                sql_check = "update runner_detail d set d.record_status = 2 where d.record_id = "+str(order[i])
                res = update_to_sql(sql_check)
                print(sql_check)
                # '0'为审核失败，检查输入的序号
                m = 0
                if res == '0':
                    my_friend.send("该记录不存在! 请检查！"+str(order[i]))
                else:
                    m = m + 1
                    sql_select = "select m.USER_NAME, d.RUN_DISTANCE, date_format(d.DATE_CREATED,'%m-%d %H:%i') as DATE_CREATED," \
                                 " t.USER_ID from runner_detail d " \
                                 "inner join runner_target t on d.target_id = t.target_id inner join " \
                                 "runner_members m on t.user_id = m.user_id where d.record_id = "+str(order[i])
                    detail = read_from_sql(sql_select)
                    detail['RUN_DISTANCE'] = [round(x, 2) for x in detail['RUN_DISTANCE']]
                    # print(sql_select)
                    detail_pass = detail[['USER_NAME', 'RUN_DISTANCE', 'DATE_CREATED']].rename(columns={
                        'USER_NAME': '用户', 'RUN_DISTANCE': '距离', 'DATE_CREATED': '记录时间'})
                    my_group.send(detail_pass)
                    my_group.send("以上记录已经被审核通过")

                    # # 审核通过同时更新目标记录表的实际跑步距离
                    # tar_update = "update runner_target t set t.distance_actually = t.distance_actually " \
                    #              "+"+str(detail_pass['距离'][0])+" where t.target_id = " \
                    #              "(select d.target_id from runner_detail d where d.record_id = "+str(order[i])+ ")"
                    # print(tar_update)
                    # update_to_sql(tar_update)
                    #
                    # # 检查是否需要修改完成状态
                    # comp_update = "update runner_target t set t.completed_status = 1 where t.is_last = 1 and " \
                    #               "t.completed_status = 0 and t.distance_actually >= t.distance_target " \
                    #               "and t.user_id = "+str(detail['USER_ID'][0])
                    # print(comp_update)
                    # update_to_sql(comp_update)

            my_friend.send("审核了"+str(m)+"条记录！")

        # 管理员审核记录不通过
        elif msg.text.lower().split(' ')[0] == 'np':
            print(msg.text)
            order = msg.text.split(' ')
            for i in range(1, len(order)):
                check_status = "select record_status from runner_detail where record_id = " + str(order[i])
                if read_from_sql(check_status)['record_status'][0] != '3':
                    sql_check = "update runner_detail d set d.record_status = 3 where d.record_id = " + str(order[i])
                    res = update_to_sql(sql_check)
                    print(sql_check)
                    # '0'为审核失败，检查输入的序号
                    m = 0
                    if res == '0':
                        my_friend.send("该记录不存在! 请检查！" + str(order[i]))
                    else:
                        m = m + 1
                        sql_select = "select m.USER_NAME, d.RUN_DISTANCE, date_format(d.DATE_CREATED,'%m-%d %H:%i') as DATE_CREATED, " \
                                     "t.USER_ID from runner_detail d " \
                                     "inner join runner_target t on d.target_id = t.target_id inner join " \
                                     "runner_members m on t.user_id = m.user_id where d.record_id = " + str(order[i])
                        detail = read_from_sql(sql_select)
                        detail['RUN_DISTANCE'] = [round(x, 2) for x in detail['RUN_DISTANCE']]
                        # print(sql_select)
                        detail_pass = detail[['USER_NAME', 'RUN_DISTANCE', 'DATE_CREATED']].rename(columns={
                            'USER_NAME': '用户', 'RUN_DISTANCE': '距离', 'DATE_CREATED': '记录时间'})
                        my_group.send(detail_pass)
                        my_group.send("以上记录管理员审核未通过")

                        # 审核通过同时更新目标记录表的实际跑步距离
                        tar_update = "update runner_target t set t.distance_actually = t.distance_actually " \
                                     "-" + str(detail_pass['距离'][0])+" where t.target_id = " \
                                     "(select d.target_id from runner_detail d where d.record_id = "+str(order[i])+ ")"
                        print(tar_update)
                        update_to_sql(tar_update)

                        # 检查是否需要修改完成状态
                        comp_update = "update runner_target t set t.completed_status = 1 where t.is_last = 1 and " \
                                      "t.completed_status = 0 and t.distance_actually >= t.distance_target " \
                                      "and t.user_id = "+str(detail['USER_ID'][0])
                        print(comp_update)
                        update_to_sql(comp_update)
                else:
                    my_friend.send("该记录状态已为不通过，无法重复修改！记录ID为：" + str(order[i]))

            my_friend.send(str(m) + "条记录审核不通过！")

        # # 管理员查看本周用户状态
        # elif msg.text.lower() == 'us':
        #     sql_us = "select m.USER_ID,m.USER_NAME,m.RUN_STATUS from runner_members m;"
        #     run_status = read_from_sql(sql_us)
        #     run_status.rename(columns={'USER_ID': '用户id', 'USER_NAME': '用户', 'RUN_STATUS': '状态'},
        #                       inplace=True)
        #     my_friend.send(run_status)
        #     my_friend.send("其中，1:跑步状态，2:临时观众，3:长期观众")
        #
        # # 管理员申请将谁加入白名单
        # elif msg.text.lower().split(' ')[0] == 'addw':
        #     order = msg.text.split(' ')
        #     for i in range(1, len(order)):
        #         sql_check = "update runner_members m set m.RUN_STATUS = 2 where m.USER_ID = " + str(order[i])
        #         res = update_to_sql(sql_check)
        #         print(sql_check)
        #         # '0'为审核失败，检查输入的序号
        #         if res == '0':
        #             my_friend.send("该用户不存在! 请检查！" + str(order[i]))
        #         else:
        #             sql_aw = "select m.USER_NAME from runner_members m where m.USER_ID = " + str(order[i])
        #             user = read_from_sql(sql_aw)
        #             my_friend.send("该用户"+str(user['USER_NAME'][0])+"本周被列入临时观众席！")
        #             my_group.send("该用户" + str(user['USER_NAME'][0]) + "本周被列入临时观众席！")

        else:
            my_friend.send("无法识别输入的指令！")
            my_friend.send("查看本周跑步记录列表请输入:re"+'\n'+"通过某条记录请输入:pass 记录id"+'\n'
                            + "不通过某条记录请输入:np 记录id" + '\n' + "查看群成员本周状态请输入：us"+ '\n' + "添加成员到白名单：addw 用户id")
    else:
        print(msg.text)
        print (msg.member)
        print (msg.member.name)
        inf = msg.text.split('\u2005')[1:]
        inform = inf[0].split(' ') # inform: ['add', '5', '0530']

        # 添加跑步记录操作
        if inform[0].lower() == 'add':
            print(inform)
            print (type(inform[1]))
            isdigit = check_str(inform)
            # 若输入不是数字或输入数字异常或参数输入过多
            # 当用户只输入公里数时
            if len(inform) <= 2:
                if (isdigit == '1') or (float(inform[1]) > 100) or (float(inform[1]) < 3):
                    my_group.send("请检查输入格式！格式如：'add 5 0630'")
                else:
                    sql_user = "select * from runner_members t where t.user_name = '" + msg.member.name + "'"
                    print (sql_user)
                    uid = read_from_sql(sql_user)['USER_ID'][0]
                    print(uid)
                    print(type(uid))
                    sql_target = 'select * from runner_target t where t.is_last = 1 and t.user_id = ' + str(uid)
                    print(sql_target)
                    tid = read_from_sql(sql_target)['TARGET_ID'][0]
                    # 考虑只输入公里数的情况
                    sql = 'insert into runner_detail (RECORD_STATUS,USER_ID,TARGET_ID,RUN_DISTANCE) values ("2",' + \
                          str(uid) + ',' + str(tid) + ',' + inform[1] + ')'
                    print (sql)
                    insert_to_sql(sql)
                    my_group.send("添加成功！")
                    # my_friend.send("新增一条记录，请审核！")

                    # 审核通过同时更新目标记录表的实际跑步距离
                    tar_update = "update runner_target t set t.distance_actually = t.distance_actually " \
                                 "+" + str(inform[1]) + " where t.target_id = " + str(tid)
                    print(tar_update)
                    update_to_sql(tar_update)

                    # 检查是否需要修改完成状态
                    comp_update = "update runner_target t set t.completed_status = 1 where t.is_last = 1 and " \
                                  "t.completed_status = 0 and t.distance_actually >= t.distance_target " \
                                  "and t.user_id = " + str(uid)
                    print(comp_update)
                    update_to_sql(comp_update)

            # 当用户输入公里数和配速时
            elif len(inform) >= 3:
                if (isdigit == '1')or (float(inform[1]) > 100) or (len(inform) > 3) or (float(inform[1]) < 3) or (float(inform[2]) < 1):
                    my_group.send("请检查输入格式！格式如：'add 5 0630'")
                else:
                    sql_user = "select * from runner_members t where t.user_name = '"+msg.member.name+"'"
                    print (sql_user)
                    uid = read_from_sql(sql_user)['USER_ID'][0]
                    print(uid)
                    print(type(uid))
                    sql_target = 'select * from runner_target t where t.is_last = 1 and t.user_id = '+str(uid)
                    print(sql_target)
                    tid = read_from_sql(sql_target)['TARGET_ID'][0]
                    sql = 'insert into runner_detail (RECORD_STATUS，USER_ID,TARGET_ID,RUN_DISTANCE,RUN_SPEED) ' \
                          'values ("2",'+str(uid)+','+str(tid)+',' + inform[1]+','+inform[2]+')'
                    print (sql)
                    insert_to_sql(sql)
                    my_group.send("添加成功！")
                    # my_friend.send("新增一条记录，请审核！")

                    # 审核通过同时更新目标记录表的实际跑步距离
                    tar_update = "update runner_target t set t.distance_actually = t.distance_actually " \
                                 "+" + str(inform[1]) + " where t.target_id = " + str(tid)
                    print(tar_update)
                    update_to_sql(tar_update)

                    # 检查是否需要修改完成状态
                    comp_update = "update runner_target t set t.completed_status = 1 where t.is_last = 1 and " \
                                  "t.completed_status = 0 and t.distance_actually >= t.distance_target " \
                                  "and t.user_id = " + str(uid)
                    print(comp_update)
                    update_to_sql(comp_update)

        # 查看本群本周跑步完成情况
        elif inform[0].lower() == 'vi':
            sql_vi = "select m.USER_NAME, d.RUN_DISTANCE,date_format(d.DATE_CREATED,'%m-%d %H:%i') as DATE_CREATED " \
                     "from runner_detail d inner join " \
                     "runner_target t on d.target_id = t.target_id inner join " \
                     "runner_members m on t.user_id = m.user_id where t.is_last=1 and d.RECORD_STATUS=2 " \
                     "order by d.DATE_CREATED asc;"
            detail = read_from_sql(sql_vi)
            detail['RUN_DISTANCE'] = [round(x, 2) for x in detail['RUN_DISTANCE']]
            print(detail)
            detail.rename(columns={'USER_NAME': '用户', 'RUN_DISTANCE': '距离', 'DATE_CREATED': '记录时间'}, inplace = True)
            if detail.empty:
                my_group.send("本周还没人跑步，赶紧去跑步啊！")
            else:
                my_group.send(detail)

        # 查看本周用户状态
        elif inform[0].lower() == 'us':
            sql_us = "select m.USER_ID,m.USER_NAME,m.RUN_STATUS from runner_members m;"
            run_status = read_from_sql(sql_us)
            run_status.rename(columns={'USER_ID': '用户id', 'USER_NAME': '用户', 'RUN_STATUS': '状态'},
                              inplace=True)
            my_group.send(run_status)
            my_group.send("其中，1:跑步状态，2:临时观众，3:长期观众")

        # 申请加入白名单
        elif inform[0].lower() == 'addw':

            sql_user = "select * from runner_members t where t.user_name = '" + msg.member.name + "'"
            print (sql_user)
            uid = read_from_sql(sql_user)['USER_ID'][0]
            uname = read_from_sql(sql_user)['USER_NAME'][0]
            print(uid)
            sql_check = "update runner_members m set m.RUN_STATUS = 2 where m.USER_ID = " + str(uid)
            res = update_to_sql(sql_check)
            if res == "0":
                my_group.send("该用户" + str(uname) + "不存在，请检查数据库！！")
            print(sql_check)
            my_group.send("该用户" + str(uname) + "本周被列入临时观众席！")
        else:
            my_group.send("无法识别输入的指令！")
            my_group.send("添加跑步记录请输入：@杨超越 add 公里数 配速，如@杨超越 add 5 0630 "+'\n'+"查看跑步记录请输入：@杨超越 vi"
                          + '\n' + "查看群成员本周状态请输入：@杨超越 us"+ '\n' + "添加成员到白名单：@杨超越 addw")
            return


# 堵塞进程，直到结束消息监听 (例如，机器人被登出时)
bot.join()