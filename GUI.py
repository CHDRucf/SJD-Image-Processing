from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from tkinter import filedialog, messagebox, Tk
from textCropping import crop
from matplotlib import pyplot as plt
import sys, time, pytesseract, os, pathlib, cv2, pkg_resources.py2_warn
import numpy as np


os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

class Ui_MainWindow(object):

    directoryToProcess = ""
    fileToProcess = []
    placeToSave = ""

    def selectDirectory(self):
        directory = Tk()

        # iconifies the root window
        directory.iconify()

        directory.filename = filedialog.askdirectory(title = "Select a directory to process")
        Ui_MainWindow.directoryToProcess = directory.filename
        Ui_MainWindow.fileToProcess = ""

        # removes the root window
        directory.withdraw()

    def selectImage(self):
        imageToProcess = Tk()

        # iconifies the root window
        imageToProcess.iconify()

        imageToProcess.filename = filedialog.askopenfilename(title = "Select an image file", filetypes = (("TIF Files", "*.tif") , ("TIFF Files", "*.tiff")))
        Ui_MainWindow.fileToProcess = (imageToProcess.filename)
        Ui_MainWindow.directoryToProcess = ""

        # removes the root window
        imageToProcess.withdraw()

    def saveHere(self):
        saveLocation = Tk()

        # iconifies the root window
        saveLocation.iconify()

        saveLocation.filename = filedialog.askdirectory( title = "Select a save location")
        Ui_MainWindow.placeToSave = saveLocation.filename

        # removes the root window
        saveLocation.withdraw()

    def startWorking(directoryToProcess, fileToProcess, placeToSave):

        # if a directory was selected then process it
        if directoryToProcess != "":

            # getting the files that are inside of the directory
            files = []
            for root, dirs, filess in os.walk(directoryToProcess):
                for file in filess:
                    files.append(os.path.join(root, file))

            if len(files) == 1:
                crop(files[0], placeToSave)

            else:
                crop(files, placeToSave)

        else:
            crop(fileToProcess, placeToSave)

    def confirmValues(self):

        if Ui_MainWindow.directoryToProcess == "" and Ui_MainWindow.fileToProcess == "":
            box = Tk()
            box.withdraw()
            box = messagebox.showinfo('Information','Please pick at least one file or directory before continuing.')
            return


        if Ui_MainWindow.placeToSave == "":
            box = Tk()
            box.withdraw()
            box = messagebox.showinfo('Information','Please pick a save location.')
            return


        Ui_MainWindow.startWorking(
        Ui_MainWindow.directoryToProcess,
        Ui_MainWindow.fileToProcess,
        Ui_MainWindow.placeToSave)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.setFixedSize(455, 210)

        self.setStyleSheet("background-color: #404040; color: white;")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("pega.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        MainWindow.setWindowIcon(icon)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.directoryOfImages = QtWidgets.QPushButton(self.centralwidget)
        self.directoryOfImages.setGeometry(QtCore.QRect(70, 40, 101, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.directoryOfImages.sizePolicy().hasHeightForWidth())
        self.directoryOfImages.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.directoryOfImages.setFont(font)
        self.directoryOfImages.setObjectName("directoryOfImages")
        self.directoryOfImages.setStyleSheet("background-color:gray;");


        self.singleImage = QtWidgets.QPushButton(self.centralwidget)
        self.singleImage.setGeometry(QtCore.QRect(290, 40, 101, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.singleImage.setFont(font)
        self.singleImage.setObjectName("singleImage")
        self.singleImage.setStyleSheet("background-color:gray;");

        self.saveLocation = QtWidgets.QPushButton(self.centralwidget)
        self.saveLocation.setGeometry(QtCore.QRect(180, 100, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.saveLocation.setFont(font)
        self.saveLocation.setObjectName("saveLocation")
        self.saveLocation.setStyleSheet("background-color:gray;");

        self.Process = QtWidgets.QPushButton(self.centralwidget)
        self.Process.setGeometry(QtCore.QRect(180, 160, 101, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.Process.setFont(font)
        self.Process.setObjectName("Process")
        self.Process.setStyleSheet("background-color:gray;");

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 466, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.directoryOfImages.clicked.connect(MainWindow.selectDirectory)
        self.singleImage.clicked.connect(MainWindow.selectImage)
        self.saveLocation.clicked.connect(MainWindow.saveHere)
        self.Process.clicked.connect(MainWindow.confirmValues)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Crop"))
        MainWindow.setWindowIcon(QtGui.QIcon(""))
        self.directoryOfImages.setText(_translate("MainWindow", "Directory"))
        self.singleImage.setText(_translate("MainWindow", "Image"))
        self.saveLocation.setText(_translate("MainWindow", "Save"))
        self.Process.setText(_translate("MainWindow", "Process"))


class App(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)


app = QApplication(sys.argv)
form = App()
form.show()
app.exec_()
