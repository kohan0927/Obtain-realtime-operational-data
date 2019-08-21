#coding:utf-8

# 必要的系統模組
from PyQt5.QtCore import pyqtSignal, QThread
from pymodbus.client.sync import ModbusTcpClient as ModClient
import time
import datetime
import threading

# 自訂的模組
import detection
import HMIFTP
import HMIFTP1

sleepTimeFTP = 0
foundFTPTotal = 0
strHMIIP = ""
exportFolder = ""

isStopThread = True
isStopGUIThread = True
updateTrigger = False

sleepBreak = threading.Event()
sleepGUIBreak = threading.Event()

class StartThreadFunc(QThread):
    #e = threading.Event()
    countChanged = pyqtSignal(int)

    def __init__(self, uiObj):
        QThread.__init__(self)
        self.mainUI = uiObj

    def run(self):
        global isStopThread, updateTrigger, sleepBreak

        textCount = 0
        while isStopThread == False: #重複執行main.startThread
            if textCount == 5:
                self.mainUI.ExportOperationLOG()
                self.mainUI.listWidget.clear()
                textCount = 0

            self.mainUI.listWidget.addItem("========HMI接続中========")
            timeMSG = "現在時間：{0}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
            self.mainUI.listWidget.addItem(timeMSG)

            isConnection = 1
            try:
                client = ModClient(strHMIIP, port=8010)
                client.read_holding_registers(0,1)
                client.close()
            except:
                self.mainUI.listWidget.addItem("HMIに接続出来ません")
                isConnection = 0

            if isConnection == 1:
                HMIFTP.stopConnection = False
                #HMIFTP.connection(self.mainUI, strHMIIP, exportFolder)


                HMIFTP1.stopConnection = False
                #HMIFTP1.connection(self.mainUI, strHMIIP, exportFolder)

                # LTData_Out.txt読み込む
                try:
                    detection.ActionOut(self.mainUI, strHMIIP)
                except:
                    pass

                # Meas_start/fin読み込む
                try:
                    detection.ActionMeas(self.mainUI, strHMIIP)
                except:
                    pass

                # if リセット実行, LTDataInit書き込み
                detection.ActionInit(self.mainUI, strHMIIP)

                # Check Abort.txt
                try:
                    detection.ActionAbort(self.mainUI, strHMIIP)
                except:
                    pass


            #HMIFTP.stopConnection = False
            #HMIFTP.connection(self.mainUI, strHMIIP, sourceFolder)

            updateTrigger = True
            sleepBreak.wait(timeout=sleepTimeFTP)
            self.countChanged.emit(True) #也可傳變數

            textCount = textCount + 1

        if isStopThread == True:
            time.sleep(1)
            HMIFTP.stopConnection = True
            HMIFTP1.stopConnection = True

            self.mainUI.listWidget.addItem("\n=======HMI接続停止=======")
            timeMSG = "現在時間：{0}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
            self.mainUI.listWidget.addItem(timeMSG)
            self.mainUI.pushButton_stop_FTP.hide()
            self.mainUI.label_start.hide()
            self.mainUI.pushButton_start_FTP.show()
            self.mainUI.pushButton_sourceFolder.setEnabled(True)
            self.mainUI.pushButton_exportFolder.setEnabled(True)
