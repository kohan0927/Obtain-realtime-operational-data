#coding:utf-8

# 必要的系統模組
import os

# 自訂的模組
import accessfile
import modbusClient

sourceFolder = ""
exportFolder = ""

def ActionOut(self, strHMIIP):
    print("sourceFolder")
    print(sourceFolder)
    for currentFile in os.listdir(sourceFolder):  # listdir()將指定路徑裡的檔案都取出
        date_string = currentFile.split(".")[0::][0]

        if date_string == "LTDataOut":
            fullPath = sourceFolder + "/" + currentFile
            cmmX, cmmY, cmmZ, probingCnt, collisionCnt = accessfile.DataOut(self, fullPath)

            modbusClient.SetOutString(self, strHMIIP, cmmX, cmmY, cmmZ, probingCnt, collisionCnt)
            self.listWidget.addItem("LTDataOut更新")

            os.remove(fullPath)

def ActionMeas(self, strHMIIP):
    isStart = 0

    for currentFile in os.listdir(sourceFolder):  # listdir()將指定路徑裡的檔案都取出
        if currentFile == "meas_start.txt":
            isStart = 1

            # 先讀LW 若是0則顯示並LW=1。 若是1 代表之前已經開始 就不用顯示了
            isStart_HMI = modbusClient.CheckStart(self, strHMIIP)
            #isStart_HMI[1]

            # ------------------------------------------------
            #if isStart_HMI == 0:
            modbusClient.SetStart(self, strHMIIP, isStart)
            planid, serialno, operator, checkreason = accessfile.MeasStart(self, sourceFolder)
            modbusClient.SetStartString(self, strHMIIP, planid, serialno, operator, checkreason)

            if isStart_HMI == 0:
                self.listWidget.addItem("測定開始")
            else:
                self.listWidget.addItem("測定更新")
            #------------------------------------------------

            deletefile = sourceFolder + "//" + "meas_start.txt"
            os.remove(deletefile)

    for currentFile in os.listdir(sourceFolder):  # listdir()將指定路徑裡的檔案都取出
        if currentFile == "meas_fin.txt":
            #if isStart == 1:
                #deletefile = sourceFolder + "//" + "meas_start.txt"
                #os.remove(deletefile)
            isStart = 0
            # 寫LW=0
            modbusClient.SetStart(self, strHMIIP, isStart)
            self.listWidget.addItem("測定終了")

            deletefile = sourceFolder + "//" + "meas_fin.txt"
            os.remove(deletefile)
            #else:
            #    deletefile = sourceFolder + "//" + "meas_fin.txt"
            #    os.remove(deletefile)

            #modbusClient.SetClear(self, strHMIIP)

def ActionInit(self, strHMIIP):
    modbusClient.CheckReset(self, strHMIIP, exportFolder)

def ActionAbort(self, strHMIIP):
    isAbort = 0

    for currentFile in os.listdir(sourceFolder):  # listdir()將指定路徑裡的檔案都取出
        if currentFile == "meas_abort.txt":
            if modbusClient.CheckHome(self, strHMIIP) == 0: #If home is off 森松さん
                isAbort = 1

                # 先讀LW 若是0則顯示並LW=1。 若是1 代表之前已經開始 就不用顯示了
                isAbort_HMI = modbusClient.CheckAbort(self, strHMIIP)

                if isAbort_HMI == 0:
                    modbusClient.SetAbort(self, strHMIIP, isAbort)
                    self.listWidget.addItem("測定異常開始")

    # 要取得HMI home信號做判斷
    if modbusClient.CheckHome(self, strHMIIP) == 1:
        #if isAbort == 1:
        #    print("come1111")
        #    deletefile = sourceFolder + "//" + "meas_abort.txt"
        #    os.remove(deletefile)
        isAbort_HMI = modbusClient.CheckAbort(self, strHMIIP)
        if isAbort_HMI == 1:
            isAbort = 0

                # 寫LW=0
            modbusClient.SetAbort(self, strHMIIP, isAbort)
            #    print("com222")
            self.listWidget.addItem("測定異常終了")

            #deletefile = sourceFolder + "//" + "meas_abort.txt"
            #os.remove(deletefile)
