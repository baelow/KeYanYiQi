from insapp_ui import *
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, QTimer, pyqtSignal
# import datatime
import insapp_class
import sys
import datetime


class LoginWindows(QMainWindow):
    def __init__(self):
        self.start_work_day = None
        self.st_time = None
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Instrument reservation')
        self.setWindowIcon(QIcon(r'./logo.ico'))
        self.mytimer = QTimer()
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.loadinfor()
        self.ui.printwin.hide()
        self.ui.pushButton_2.hide()
        self.ui.disp_contrast_time.hide()
        self.ui.pushButton.clicked.connect(self.dowork)
        self.ui.pushButton_2.clicked.connect(self.goback)
        self.mytimer.timeout.connect(self.show_contrast_time)
        self.show()

    def loadinfor(self):
        try:
            with open('./d.dat', 'r') as f:
                list = f.read().splitlines()
            self.ui.lineEdit.setText(list[0])
            self.ui.lineEdit_2.setText(list[1])
            self.ui.lineEdit_3.setText(list[2])
            self.ui.lineEdit_4.setText(list[3])
            self.ui.lineEdit_5.setText(list[4])
            self.ui.lineEdit_6.setText(list[5])
        except:
            return None

    def saveinfor(self, list):
        writelist = '\n'.join(list)
        with open('./d.dat', 'w') as f:
            f.write(writelist)

    def goback(self):
        self.ui.printwin.hide()
        self.ui.groupBox.show()
        self.ui.pushButton.show()
        self.ui.pushButton_2.hide()
        self.ui.disp_contrast_time.hide()
        self.ui.disp_contrast_time.setText('')
        self.mytimer.stop()
        self.mythread.terminate()
        self.output(f'程序已被用户强制终止')

    def nextpage(self):
        # 显示log界面
        self.ui.printwin.show()
        self.ui.groupBox.hide()
        self.ui.pushButton.hide()
        self.ui.pushButton_2.show()
        self.ui.disp_contrast_time.show()

    def output(self, infor):
        nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        newinfor = "【" + nowtime + "】 " + infor + "\n"
        allinfor = self.ui.printwin.toPlainText() + newinfor
        self.ui.printwin.setPlainText(allinfor)

    def show_contrast_time(self):
        # 检查子进程是否在运行
        if self.mythread.isRunning():
            nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            target_time = (self.start_work_day + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + ' ' + self.st_time
            show_time = '>>> ' + target_time + ' || ' + nowtime
            self.ui.disp_contrast_time.setText(show_time)

    def getdate(self, time_interval):
        temp_date = datetime.datetime.now()  # 获取当前时间 年月日时分秒
        date1 = (temp_date + datetime.timedelta(days=+int(time_interval))).strftime("%Y-%m-%d")  # 获取当前日期的后一天日期)
        return date1

    def login_check(self, un, pw):
        myinsapply = insapp_class.ApplyIns(un, pw, "", "", "", "")
        result = myinsapply.login()
        if 'false' in result and '验证码' not in result:
            self.output('登录失败,请检查密码或账号是否正确')
            QtWidgets.QMessageBox.critical(self, "错误", '登录失败,请检查密码或账号是否正确')
            return 0
        elif 'false' in result and '验证码' in result:
            self.output(f'请打开网页正确登录一次，以避免验证码显示,{result}\n 仪器预约地址为：http://210.31.67.135/')
            QtWidgets.QMessageBox.critical(self, "错误",
                                           f'请打开网页正确登录一次，以避免验证码显示,{result}\n 仪器预约地址为：http://210.31.67.135/')
            return 0
        elif '成功' in result:
            return 1
        else:
            self.output(f"ERROR {result}")
            QtWidgets.QMessageBox.critical(self, "错误", f"ERROR {result}")
            return 0

    def dowork(self):
        self.start_work_day = datetime.datetime.today()
        # 获取信息
        un = self.ui.lineEdit.text()
        pw = self.ui.lineEdit_2.text()
        yiqi_id = self.ui.lineEdit_3.text()
        riqi_num = self.ui.lineEdit_4.text()
        self.st_time = start_time = self.ui.lineEdit_5.text()
        ktz = self.ui.lineEdit_6.text()
        send_to_thread = {
            'un': un, 'pw': pw, 'yiqi_id': yiqi_id, 'riqi_num': riqi_num, 'start_time': start_time, 'ktz': ktz
        }
        if '' not in send_to_thread.values():
            # 基础登录信息检查
            if self.login_check(un, pw):
                self.saveinfor(send_to_thread.values())
                self.nextpage()
                self.output(
                    f"您将在次日{start_time}预约{riqi_num}天后({self.getdate(riqi_num)})的仪器，仪器id/name为{yiqi_id}")
                # 显示结束和当前时间
                self.mytimer.start(1000)
                # 程序执行
                self.mythread = my_thread(send_to_thread)  # 引入多进程
                self.mythread.signal_out.connect(self.output)
                self.mythread.start()

        else:
            QtWidgets.QMessageBox.critical(self, "错误", "信息输入不全，请重新输入")


class my_thread(QThread):
    signal_out = pyqtSignal(str)

    def __init__(self, information):
        super(my_thread, self).__init__()
        self.information = information

    def run(self):
        myinsapply = insapp_class.ApplyIns(self.information['un'], self.information['pw'], self.information['yiqi_id'],
                                           self.information['riqi_num'],
                                           self.information['start_time'], self.information['ktz'])
        # 执行任务
        self.signal_out.emit(
            f"正在申请中~~~，请稍后，请勿关闭计算机和本软件,程序将在{self.information['start_time']}执行预约并输出结果")
        result = myinsapply.run_schedule()
        self.signal_out.emit(result)


if __name__ == "__main__":
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = LoginWindows()
    sys.exit(app.exec_())
