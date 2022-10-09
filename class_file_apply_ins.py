import datetime
import re
import time
import requests
import random
import schedule


class ApplyIns:
    def __init__(self, un, pw, equipmentID, apply_day_later, starttime):
        self.username = un
        self.password = pw
        self.equipmentID = equipmentID
        self.apply_day_later = apply_day_later
        self.time_setting = starttime
        self.cook = None
        self.cook2 = None
        self.cook3 = None
        self.bookday = None
        self.GoOn = None
        self.over = None
        self.result_show = []

    def deal_equipmentID(self):
        if self.equipmentID == 'ZETA':
            self.equipmentID = 'f8cd1e48-6bc4-4226-a623-e9db326452ab'  # zeta
        elif self.equipmentID == 'LC':
            self.equipmentID = '770b0366-4552-452e-bb95-475d1701e340'  # 3200
        elif self.equipmentID == 'LCMSMS':
            self.equipmentID = 'c26681cc-0590-4db7-a94a-2986b44673cc'  # 4500

    def time_pre(self, timestr):
        time_str = '2022-04-01 ' + timestr
        time_sec = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S')) - 10
        timeArray = time.localtime(time_sec)
        time2 = time.strftime('%H:%M:%S', timeArray)
        return time2

    def login_pre(self):
        # global cook
        header = {
            'User-Agernt': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'Host': '210.31.67.135', 'Connection': 'keep-alive'}
        url = 'http://210.31.67.135/Equipment/Show?Id=770b0366-4552-452e-bb95-475d1701e340&ParUrl=undefined'
        r = requests.get(url=url, headers=header)
        self.cook = re.findall('(ASP[\s\S]*?)\sfor', str(r.cookies))[0]

    def login(self):
        # global cook2
        url2 = 'http://210.31.67.135/Account/LoginSubmit'
        postdata = {
            'LoginName': self.username,
            'LoginPassword': self.password,  # '%2BHqrhJteMzkF2odX45F0Hw%3D%3D',
            'VeriType': 'TopLogin',
            'IsRememberMe': 'false',
        }

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '178',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': self.cook,
            'Host': '210.31.67.135',
            'Origin': 'http://210.31.67.135',
            'Referer': 'http://210.31.67.135/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        r = requests.post(url=url2, headers=headers, data=postdata)
        r.encoding = 'utf-8'
        state = r.text
        print('登陆时间为：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(re.findall('"msg":"(.*?)"', state)[0])
        self.cook2 = re.findall('(.ASP[\s\S]*?)\sfor', str(r.cookies))[0]

    def date(self):
        date1 = time.time()
        date = int((date1 - int(time.time())) * 1000)
        return str(date)

    def mstime(self):
        ms = str(int(time.time() * 1000))
        return ms

    def report(self, data):
        with open('report.txt', 'w') as f:
            f.write(data.text)
            f.close()
        print('已生成预约报告，请查阅')

    def get_date(self, time_interval):
        """
        :param date:                    间隔的时间 整型  前几天 为负数 100 后几天为正数 -100
        :param time_interval:           字符类型时间 年月日   ‘2020-01-01’
        :return:                        字符类型时间 年月日   ‘2020-01-01’
        """
        temp_date = datetime.datetime.now()  # 获取当前时间 年月日时分秒
        date1 = (temp_date + datetime.timedelta(days=+time_interval)).strftime("%Y-%m-%d")  # 获取当前日期的后一天日期)
        return date1

    def apply(self):
        # global GoOn
        # global cook3
        times = time.time()
        ## csrf 传入服务器
        url = 'http://210.31.67.135/PersonCenter/UserCurrentSkin?date=' + self.date() + '&_=' + self.mstime()
        csrf = str(int(random.random() * 999999999))
        self.cook3 = 'cook' + ';' + self.cook2 + ';' + csrf
        header = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': self.cook3,
            'Host': '210.31.67.135',
            'Referer': 'http://210.31.67.135/PersonCenter?CenterBoxUrl=/Equipment/AppointmentBoxIndex%3Fid%3D' + self.equipmentID + '%26time%3D304',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'X-CSRFToken': csrf,
            'X-Requested-With': 'XMLHttpRequest'
        }
        r = requests.get(url=url, headers=header)
        # print(r.text)

        ## 预约申请 #########################################################################
        Date = self.date()
        booktime_demo = '2022-04-08 00:00:00,2022-04-08 01:00:00,2022-04-08 02:00:00,2022-04-08 03:00:00,2022-04-08 04:00:00,2022-04-08 05:00:00,2022-04-08 06:00:00,2022-04-08 07:00:00,2022-04-08 08:00:00,2022-04-08 09:00:00,2022-04-08 10:00:00,2022-04-08 11:00:00,2022-04-08 12:00:00,2022-04-08 13:00:00,2022-04-08 14:00:00,2022-04-08 15:00:00,2022-04-08 16:00:00,2022-04-08 17:00:00,2022-04-08 18:00:00,2022-04-08 19:00:00,2022-04-08 20:00:00,2022-04-08 21:00:00,2022-04-08 22:00:00,2022-04-08 23:00:00'
        booktime = re.sub(r'\d+-\d+-\d+', self.bookday, booktime_demo)
        if self.GoOn == 0:
            print('当前预约的日期为' + re.match('\d+-\d+-\d+', booktime).group())
        header = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': self.cook3,
            'Host': '210.31.67.135',
            'Referer': 'http://210.31.67.135/Equipment/AppointmentBoxContainer/' + self.equipmentID + '?userParameters=id:' + self.equipmentID + '+csrftoken:' + csrf + 'HTTP_X_CSRFTOKEN:' + csrf + '&amp;date=' + Date,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'X-CSRFToken': csrf,
            'X-Requested-With': 'XMLHttpRequest'
        }
        # 获取表格信息 ＋ ID
        url_list = 'http://210.31.67.135/Appointment/AppointmentUserRelativeInfo'
        formdata_list = {
            'equipmentTimeAppointmemtMode': '0',
            'equipmentId': self.equipmentID,
            'date': self.date()
        }
        # 获取subject ID信息
        r0 = requests.post(headers=header, url=url_list, data=formdata_list)
        SubjectId = re.findall('"Id":"(.*?)","Name"', r0.text)[0]

        ## 提交信息
        formdata0 = {
            'subjectId': SubjectId,
            'time': self.date()
        }
        formdata = {
            'isSelectTimeScope': 'false',
            'beginTime': time.strftime('%Y-%m-%d', time.localtime(time.time())) + ' 0:0',
            'endTime': time.strftime('%Y-%m-%d', time.localtime(time.time())) + ' 0:0',
            'EquipmentId': self.equipmentID,
            'AppointmentTimes': booktime,
            'SubjectName': '李艳霞课题组',
            'UsedNature': 'do experiment',
            'date': self.date()
        }
        formdata1 = {
            'SubjectId': SubjectId,
            'UseNature': '0',
            'ExperimentationContent': 'experiment',
            'isSelectTimeScope': 'false',
            'beginTime': self.bookday + ' 0:0',
            'endTime': self.bookday + ' 0:0',
            'AppointmentStep': '60',
            'AppointmentTimes': booktime,
            'EquipmentId': self.equipmentID,
            'AppointmentFeeTips': 'false'
        }

        url0 = 'http://210.31.67.135/Subject/GetSubjectProjectList'
        content = {
            'subjectId': self.equipmentID,
            'time': self.date()
        }
        url = 'http://210.31.67.135/Appointment/AppointmentTotalInfo'
        url1 = 'http://210.31.67.135/Appointment/Appointment'

        # requests.post(headers=header, url=url0, data=formdata0)
        r1 = requests.post(headers=header, url=url, data=formdata)
        r2 = requests.post(headers=header, url=url1, data=formdata1)
        # print(r1.text)

        # report(r1)
        # print(r2.text)
        # return r2
        timee = time.time()
        if '您的预约已提交,请在预约时间前24小时登录确认' in r2.text:
            print('预约成功，请前往系统查看')
            self.result_show.append( '预约成功，请前往系统查看')
        elif '还未到提前开放预约时间' in r2.text:
            print('系统提示：还未到提前开放预约时间 \n 即将继续申请...本轮申请时间耗时：%.5f s' % (timee - times))
            self.result_show.append('系统提示：还未到提前开放预约时间 \n 即将继续申请...本轮申请时间耗时：' + str(timee - times) + ' s')
            self.GoOn = 1
        else:
            print(r2.text)
            self.result_show.append(r2.text)

    def show_result(self):
        return self.result_show

    def task_pre(self):
        self.deal_equipmentID()
        self.bookday = self.get_date(self.apply_day_later)
        self.login_pre()
        self.login()
        self.GoOn = 0

    def task_run(self):
        ###程序执行##################################
        time.sleep(0.1)
        time1 = time.time()
        while True:
            self.apply()
            time_check = time.time() - time1
            if self.GoOn == 0:
                break
            elif time_check > 180:  # 运行时间超过60秒
                print('运行时间已达180s，仍未申请成功，请登录网页检查')
                self.result_show.append('运行时间已达180s，仍未申请成功，请登录网页检查')
                break
            else:
                time.sleep(0.1)
        self.over = 1
        time2 = time.time()
        print('本次预约用时为：' + str(time2 - time1))
        self.result_show.append('本次预约用时为：' + str(time2 - time1))

    def run_schedule(self):
        schedule.every().day.at(self.time_pre(self.time_setting)).do(self.task_pre)  # 提前10秒登录
        schedule.every().day.at(self.time_setting).do(self.task_run)
        while True:
            schedule.run_pending()
            if self.over != 1:
                time.sleep(0.1)
            else:
                break
