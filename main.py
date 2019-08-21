#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system modules
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import ctypes
import sys
import os

# self-defined module
import thread
import detection
import gui

# Japanese font
plt.rcParams['font.family'] = 'IPAPGothic'

class Main(QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        global FTP_Path, startDateSelection, endDateSelection, foundCSVTotal
        self.foundCSVTotal = []

        # Check openpath.csv
        try:
            openPath = pd.read_csv('./openpath.csv')
        except:
            ctypes.windll.user32.MessageBoxW(0, "openpath.csvのファイル所在不明", "エラー", 0)
            sys.exit()

        #### Source Path ####
        try:
            sourcePath_s = list(openPath)[0]
        except:
            ctypes.windll.user32.MessageBoxW(0, "openpath.csvのカラムの名はPATHが必要", "エラー", 0)
            sys.exit()

        if sourcePath_s == "Source Path":
            try:
                # Source location
                self.lineEdit_sourceFolder.setText(openPath['Source Path'][0])
            except:
                ctypes.windll.user32.MessageBoxW(0, "PATHが間違い", "エラー", 0)
                exit()
        else:
            ctypes.windll.user32.MessageBoxW(0, "openpath.csvのカラムの名はご確認ください", "エラー", 0)
            sys.exit()

        #### Export Path ####
        try:
            exportPath_s = list(openPath)[1]
        except:
            ctypes.windll.user32.MessageBoxW(0, "openpath.csvのカラムの名はPATHが必要", "エラー", 0)
            sys.exit()

        if exportPath_s == "Export Path":
            try:
                # Source location
                self.lineEdit_exportFolder.setText(openPath['Export Path'][0])
            except:
                ctypes.windll.user32.MessageBoxW(0, "PATHが間違い", "エラー", 0)
                exit()
        else:
            ctypes.windll.user32.MessageBoxW(0, "openpath.csvのカラムの名はご確認ください", "エラー", 0)
            sys.exit()

        #### HMI IP ####
        try:
            HMIIP_s = list(openPath)[2]
        except:
            ctypes.windll.user32.MessageBoxW(0, "openpath.csvのHMIのIPが必要", "エラー", 0)
            sys.exit()

        if HMIIP_s == "HMI IP":
            try:
                # HMI IP
                self.lineEdit_HMIIP.setText(openPath['HMI IP'][0])
            except:
                ctypes.windll.user32.MessageBoxW(0, "PATHが間違い", "エラー", 0)
                exit()
        else:
            ctypes.windll.user32.MessageBoxW(0, "openpath.csvのカラムの名はご確認ください", "エラー", 0)
            sys.exit()

        # Source select button
        self.pushButton_sourceFolder.clicked.connect(lambda: self.openFolderFile())
        # Export select button
        self.pushButton_exportFolder.clicked.connect(lambda: self.exportFolderFile())
        # FTP START button
        self.pushButton_start_FTP.clicked.connect(lambda: self.connectFTP())
        # FTP STOP button
        self.pushButton_stop_FTP.clicked.connect(lambda: self.stopFTP())
        self.pushButton_stop_FTP.hide() # set to hide for the default
        # HMI connecting text
        self.label_start.hide()
        # Close app
        self.closeEvent = self.closeEvent
        # Clear message
        self.pushButton_clear.clicked.connect(lambda: self.listWidget.clear())
        # Export operation log
        self.pushButton_exportOperation.clicked.connect(lambda: self.ExportOperationLOG())
        # Reset APP
        self.pushButton_reset.clicked.connect(lambda: self.ResetAPP())

        # Automatically start
        self.connectFTP()

        self.show()

    def openFolderFile(self):  #Open HMI source file
        folderPath = os.path.dirname(self.lineEdit_sourceFolder.text())
        path = QFileDialog.getExistingDirectory(self, "ディレクトリ選択", folderPath)

        lastPath = self.lineEdit_sourceFolder.text()
        if path == "":
            if lastPath != "":
                self.lineEdit_sourceFolder.setText(lastPath)
        else:
            self.lineEdit_sourceFolder.setText(path)

        filepath = open('./openpath.csv', encoding='utf-8-sig')
        openPath = pd.read_csv(filepath)
        openPath['Source Path'][0] = self.lineEdit_sourceFolder.text()
        openPath.to_csv('./openpath.csv', index=False, encoding='utf-8-sig')

    def exportFolderFile(self):  #Open HMI export file
        folderPath = os.path.dirname(self.lineEdit_exportFolder.text())
        path = QFileDialog.getExistingDirectory(self, "ディレクトリ選択", folderPath)

        lastPath = self.lineEdit_exportFolder.text()
        if path == "":
            if lastPath != "":
                self.lineEdit_exportFolder.setText(lastPath)
        else:
            self.lineEdit_exportFolder.setText(path)

        filepath = open('./openpath.csv', encoding='utf-8-sig')
        openPath = pd.read_csv(filepath)
        openPath['Export Path'][0] = self.lineEdit_exportFolder.text()
        openPath.to_csv('./openpath.csv', index=False, encoding='utf-8-sig')

    def LabelShow(self):
        if self.pushButton_start_FTP.isHidden() == True:
            self.label_start.show()
            QTimer.singleShot(2000, lambda: self.LabelHide())

    def LabelHide(self):
        if self.pushButton_start_FTP.isHidden() == True:
            self.label_start.hide()
            QTimer.singleShot(2000, lambda: self.LabelShow())

    def ExportOperationLOG(self): # Export operation log
        outdir_LOG = './OperationLog'
        if not os.path.exists(outdir_LOG):
            os.makedirs(outdir_LOG, exist_ok=True)

        nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = outdir_LOG + '/LOG_' + nowTime + '.txt'

        with open(filename, 'a', encoding='utf-8-sig') as s: #utf8
            for i in range(self.listWidget.model().rowCount()):
                text = self.listWidget.model().data(self.listWidget.model().index(i))
                text = text + "\n"
                s.write(text)

    def connectFTP(self): # Connect HMI's FTP for realtime purpose
        # Prevention
        self.pushButton_start_FTP.hide()
        self.LabelShow()
        self.pushButton_stop_FTP.show()
        self.pushButton_sourceFolder.setDisabled(True)
        self.pushButton_exportFolder.setDisabled(True)
        self.lineEdit_HMIIP.setDisabled(True)

        sourceFolder = self.lineEdit_sourceFolder.text()
        exportFolder = self.lineEdit_exportFolder.text()
        strHMIIP = self.lineEdit_HMIIP.text()

        # 記錄下來
        filepath = open('./openpath.csv', encoding='utf-8-sig')
        openPath = pd.read_csv(filepath)
        openPath['Source Path'][0] = self.lineEdit_sourceFolder.text()
        openPath.to_csv('./openpath.csv', index=False, encoding='utf-8-sig')

        exportpath = open('./openpath.csv', encoding='utf-8-sig')
        openExport = pd.read_csv(exportpath)
        openExport['Export Path'][0] = self.lineEdit_exportFolder.text()
        openExport.to_csv('./openpath.csv', index=False, encoding='utf-8-sig')

        HMIpath = open('./openpath.csv', encoding='utf-8-sig')
        openHMI = pd.read_csv(HMIpath)
        openHMI['HMI IP'][0] = self.lineEdit_HMIIP.text()
        openHMI.to_csv('./openpath.csv', index=False, encoding='utf-8-sig')

        detection.sourceFolder = sourceFolder
        detection.exportFolder = exportFolder

        thread.exportFolder = exportFolder

        thread.strHMIIP = strHMIIP
        thread.sleepTimeFTP = 1
        thread.sleepBreak.clear()
        thread.isStopThread = False

        self.trdProcess = thread.StartThreadFunc(self)
        self.trdProcess.start()

    def stopFTP(self): # Stop FTP button
        thread.isStopThread = True
        thread.sleepBreak.set()

    def ResetAPP(self):
        isReset = ctypes.windll.user32.MessageBoxW(0, "リセットしますか？", "警告", 4)
        if isReset == 6: # Yes:6, No:7
            # Stop thread
            thread.isStopThread = True
            thread.sleepBreak.set()

            # Founded FTP list
            self.foundFTPTotal = []
            # Founded CSV list
            self.foundCSVTotal = []
            # Label start text
            self.label_start.hide()
            # FTP start show
            self.pushButton_start_FTP.show()
            # FTP start hide
            self.pushButton_stop_FTP.hide()
            self.pushButton_sourceFolder.setEnabled(True)
            self.pushButton_exportFolder.setEnabled(True)
            self.lineEdit_HMIIP.setEnabled(True)

            # kill thread
            thread.isStopThread = True
            thread.sleepBreak.set()
            thread.isStopGUIThread = True
            thread.sleepGUIBreak.set()
            thread.updateTrigger = False

            self.listWidget.addItem("アプリリセット")

    def closeEvent(self, event):
        print("アプリ閉まる!") # #sys.exit(0)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = Main()
    MainWindow.show()
    sys.exit(app.exec_())
