# -*- coding: utf-8 -*-
"""
Created on 18/10/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the open and create new analysis functions
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, numpy as np, cv2
from functions import DIC_Global
from interface import menubar, generateGrid, dockWidget, StrainAnalysis

def openPrevious(self): #when opening a previous analysis, ask for the project folder and launch the analysis widget

    flags = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
    directory = QFileDialog.getExistingDirectory(self, 'Data Folder', '', flags)

    if directory == "":
        return
    else:
        for instance in dockWidget.dockPlot.instances: #deleting dockwidget if there are
            instance.close()
            instance.deleteLater()
        dockWidget.dockPlot.instances = []

        self.filePath = os.path.dirname(directory)
        self.fileDataPath = directory

        StrainAnalysis.analyseResult(self, self)

def startNewAnalysis(self): #called when a new analysis is started

    filePathTest = QFileDialog.getOpenFileName(self, 'Select first image', '', 'Image Files (*.tif *.tiff *.bmp *.jpg *.jpeg *.png)')

    if filePathTest == '':
        return
    else: #create the file list when an image is selected

        extension = os.path.splitext(os.path.basename(filePathTest))[1]
        fileList = os.listdir(os.path.dirname(filePathTest))
        fileList = [nb for nb in fileList if nb.endswith(extension)]
        fileNameList = []

        count = 0
        for element in fileList:
            fileNameList.append('{0}'.format(element))
            count+=1

        newAnalysis = nameAnalysis(self, fileNameList, os.path.dirname(filePathTest))
        result = newAnalysis.exec_()

        if result == 1:
            menubar.menuDisabled(self)
            for instance in dockWidget.dockPlot.instances: #deleting dockwidget if there are
                instance.close()
                instance.deleteLater()
            dockWidget.dockPlot.instances = []
            self.filterFile = None
            menubar.menuCreateGridEnabled(self)
            generateGrid.createGrid(self)


class nameAnalysis(QDialog):

    def __init__(self, parent, fileNameList, filePath):

        QDialog.__init__(self)
        dialogLayout = QVBoxLayout()
        dialogLayout.setSpacing(20)
        self.setWindowTitle('Analysis Creation')
        self.setMaximumWidth(500)
        self.setMaximumHeight(600)
        self.filePath = filePath

        infoLbl = QLabel('Please verify the automatic image selection.')
        infoLbl.setAlignment(Qt.AlignCenter)

        imageLayout = QHBoxLayout()
        self.plotArea = DIC_Global.matplotlibWidget()
        self.plotArea.setMaximumHeight(300)
        self.imageList = QListView()
        self.imageList.setMinimumWidth(200)
        self.imageList.setMaximumHeight(300)
        self.imageList.setContentsMargins(0,20,0,20)
        self.imageModel = QStandardItemModel(self.imageList)
        for image in fileNameList:
            imageItem = QStandardItem(image)
            imageItem.setCheckable(True)
            imageItem.setCheckState(Qt.Checked)
            self.imageModel.appendRow(imageItem)
        self.imageList.setModel(self.imageModel)
        self.imageList.setCurrentIndex(self.imageModel.indexFromItem(self.imageModel.item(0)))
        self.imageList.clicked.connect(lambda: self.displayImage(fileNameList))
        imageLayout.addWidget(self.plotArea)
        imageLayout.addWidget(self.imageList)

        totalImageNb = len(np.atleast_1d(fileNameList))
        imageNumberLayout = QHBoxLayout()
        imageNumberLayout.setSpacing(5)
        self.fromImage = QSpinBox()
        self.fromImage.setRange(0,totalImageNb)
        toImageLbl = QLabel('to')
        self.toImage = QSpinBox()
        self.toImage.setRange(0,totalImageNb)
        invertBtn = QPushButton('Invert')
        invertBtn.clicked.connect(self.invertSelection)
        imageLbl = QLabel('Selection:')
        self.imageSelected = QLabel('-')
        totalImage = QLabel('/ '+str(totalImageNb))
        imageNumberLayout.addStretch(1)
        imageNumberLayout.addWidget(self.fromImage)
        imageNumberLayout.addWidget(toImageLbl)
        imageNumberLayout.addWidget(self.toImage)
        imageNumberLayout.addWidget(invertBtn)
        imageNumberLayout.addStretch(2)
        imageNumberLayout.addWidget(imageLbl)
        imageNumberLayout.addWidget(self.imageSelected)
        imageNumberLayout.addWidget(totalImage)
        imageNumberLayout.addStretch(1)

        analysisName = QHBoxLayout()
        analysisName.setSpacing(20)
        self.analysisLbl = QLabel('-')
        self.analysisInput = QLineEdit()
        self.analysisInput.setCursorPosition(0)
        self.analysisInput.setTextMargins(3,3,3,3)
        currentFont = self.analysisInput.font()
        currentFont.setPointSize(15)
        self.analysisInput.setFont(currentFont)
        self.analysisInput.setMinimumWidth(200)
        self.analysisInput.setMinimumHeight(40)
        validatorRx = QRegExp("\\w+")
        validator = QRegExpValidator(validatorRx, self)
        self.analysisInput.setValidator(validator)
        analysisName.addStretch(1)
        analysisName.addWidget(self.analysisLbl)
        analysisName.addWidget(self.analysisInput)
        analysisName.addStretch(1)

        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(40)
        cancelButton = QPushButton('Cancel')
        cancelButton.setMaximumWidth(100)
        cancelButton.setMinimumHeight(30)
        self.createButton = QPushButton('Start Analysis')
        self.createButton.setMinimumWidth(150)
        self.createButton.setMinimumHeight(30)
        self.createButton.setEnabled(False)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(self.createButton)
        buttonLayout.addStretch(1)

        self.analysisInput.textChanged.connect(lambda: self.textChanged(self.analysisInput.text()))
        self.createButton.clicked.connect(lambda: self.createAnalysis(parent, self.analysisInput.text()))
        cancelButton.clicked.connect(self.reject)

        dialogLayout.addWidget(infoLbl)
        dialogLayout.addLayout(imageLayout)
        dialogLayout.addLayout(imageNumberLayout)
        dialogLayout.addLayout(analysisName)
        dialogLayout.addLayout(buttonLayout)

        self.setLayout(dialogLayout)
        self.textChanged('')
        self.displayImage(fileNameList)


    def displayImage(self, fileNameList):

        self.plotArea.matPlot.cla()
        imageName = self.imageModel.itemFromIndex(self.imageList.currentIndex()).text()
        readImage = cv2.imread(self.filePath+'/'+imageName,0)
        self.plotArea.matPlot.imshow(readImage, cmap='gray')
        self.plotArea.matPlot.axes.xaxis.set_ticklabels([])
        self.plotArea.matPlot.axes.yaxis.set_ticklabels([])
        self.plotArea.draw_idle()
        self.updateSelection()

    def updateSelection(self):

        nbChecked = 0
        for image in range(self.imageModel.rowCount()):
            if self.imageModel.item(image).checkState() == Qt.Checked:
                nbChecked += 1
        self.imageSelected.setText(str(nbChecked))
        if nbChecked > 1:
            self.imageSelected.setText(str(nbChecked))
            self.textChanged(self.analysisInput.text())
        else:
            self.imageSelected.setText('<font color=red>'+str(nbChecked)+'</font>')
            self.createButton.setEnabled(False)

    def invertSelection(self):

        imageMin = min(self.fromImage.value(), self.toImage.value())
        imageMax = max(self.fromImage.value(), self.toImage.value())
        for image in range(imageMin, imageMax):
            if self.imageModel.item(image).checkState() == Qt.Checked:
                self.imageModel.item(image).setCheckState(Qt.Unchecked)
            else:
                self.imageModel.item(image).setCheckState(Qt.Checked)
        self.updateSelection()

    def textChanged(self, name):

        if name != '':
            checkName = self.filePath+'/'+name
            if os.path.exists(checkName):
                self.analysisLbl.setText('<font size=5><font color=red>Already Exist.</font></font>')
                self.createButton.setEnabled(False)
            else:
                self.analysisLbl.setText('<font size=5><font color=green>Analysis Name:</font></font>')
                if int(self.imageSelected.text()) > 1:
                    self.createButton.setEnabled(True)
        else:
            self.analysisLbl.setText('<font size=5>Analysis Name:</font>')
            self.createButton.setEnabled(False)

    def createAnalysis(self, parent, name):

        directory = self.filePath+'/'+name
        #os.makedirs(directory)
        fileNameList = []
        for image in range(self.imageModel.rowCount()):
            if self.imageModel.item(image).checkState() == Qt.Checked:
                fileNameList.append(self.imageModel.item(image).text())
        #np.savetxt(directory+'/filenamelist.dat', fileNameList, fmt="%s")
        parent.fileNameList = fileNameList
        parent.filePath = self.filePath
        parent.fileDataPath = directory
        self.accept()
