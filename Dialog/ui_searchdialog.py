# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'searchdialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SearchDialog(object):
    def setupUi(self, SearchDialog):
        SearchDialog.setObjectName("SearchDialog")
        SearchDialog.resize(436, 223)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(SearchDialog)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gbFind = QtWidgets.QGroupBox(SearchDialog)
        self.gbFind.setObjectName("gbFind")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.gbFind)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cbFindFormat = QtWidgets.QComboBox(self.gbFind)
        self.cbFindFormat.setObjectName("cbFindFormat")
        self.cbFindFormat.addItem("")
        self.cbFindFormat.addItem("")
        self.horizontalLayout.addWidget(self.cbFindFormat)
        self.cbFind = QtWidgets.QComboBox(self.gbFind)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbFind.sizePolicy().hasHeightForWidth())
        self.cbFind.setSizePolicy(sizePolicy)
        self.cbFind.setEditable(True)
        self.cbFind.setObjectName("cbFind")
        self.horizontalLayout.addWidget(self.cbFind)
        self.verticalLayout_2.addWidget(self.gbFind)
        self.gbReplace = QtWidgets.QGroupBox(SearchDialog)
        self.gbReplace.setObjectName("gbReplace")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.gbReplace)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cbReplaceFormat = QtWidgets.QComboBox(self.gbReplace)
        self.cbReplaceFormat.setObjectName("cbReplaceFormat")
        self.cbReplaceFormat.addItem("")
        self.cbReplaceFormat.addItem("")
        self.horizontalLayout_2.addWidget(self.cbReplaceFormat)
        self.cbReplace = QtWidgets.QComboBox(self.gbReplace)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbReplace.sizePolicy().hasHeightForWidth())
        self.cbReplace.setSizePolicy(sizePolicy)
        self.cbReplace.setEditable(True)
        self.cbReplace.setObjectName("cbReplace")
        self.horizontalLayout_2.addWidget(self.cbReplace)
        self.verticalLayout_2.addWidget(self.gbReplace)
        self.gbOptions = QtWidgets.QGroupBox(SearchDialog)
        self.gbOptions.setObjectName("gbOptions")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.gbOptions)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.cbBackwards = QtWidgets.QCheckBox(self.gbOptions)
        self.cbBackwards.setObjectName("cbBackwards")
        self.verticalLayout_3.addWidget(self.cbBackwards)
        self.cbPrompt = QtWidgets.QCheckBox(self.gbOptions)
        self.cbPrompt.setObjectName("cbPrompt")
        self.verticalLayout_3.addWidget(self.cbPrompt)
        self.verticalLayout_2.addWidget(self.gbOptions)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pbFind = QtWidgets.QPushButton(SearchDialog)
        self.pbFind.setDefault(True)
        self.pbFind.setObjectName("pbFind")
        self.verticalLayout.addWidget(self.pbFind)
        self.pbReplace = QtWidgets.QPushButton(SearchDialog)
        self.pbReplace.setObjectName("pbReplace")
        self.verticalLayout.addWidget(self.pbReplace)
        self.pbReplaceAll = QtWidgets.QPushButton(SearchDialog)
        self.pbReplaceAll.setObjectName("pbReplaceAll")
        self.verticalLayout.addWidget(self.pbReplaceAll)
        self.pbCancel = QtWidgets.QPushButton(SearchDialog)
        self.pbCancel.setObjectName("pbCancel")
        self.verticalLayout.addWidget(self.pbCancel)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(SearchDialog)
        self.pbCancel.clicked.connect(SearchDialog.hide)
        QtCore.QMetaObject.connectSlotsByName(SearchDialog)
        SearchDialog.setTabOrder(self.cbFind, self.cbReplace)
        SearchDialog.setTabOrder(self.cbReplace, self.cbFindFormat)
        SearchDialog.setTabOrder(self.cbFindFormat, self.cbReplaceFormat)
        SearchDialog.setTabOrder(self.cbReplaceFormat, self.cbBackwards)
        SearchDialog.setTabOrder(self.cbBackwards, self.cbPrompt)
        SearchDialog.setTabOrder(self.cbPrompt, self.pbFind)
        SearchDialog.setTabOrder(self.pbFind, self.pbReplace)
        SearchDialog.setTabOrder(self.pbReplace, self.pbReplaceAll)
        SearchDialog.setTabOrder(self.pbReplaceAll, self.pbCancel)

    def retranslateUi(self, SearchDialog):
        _translate = QtCore.QCoreApplication.translate
        SearchDialog.setWindowTitle(_translate("SearchDialog", "PyHexEditor - Find/Replace"))
        self.gbFind.setTitle(_translate("SearchDialog", "Find"))
        self.cbFindFormat.setItemText(0, _translate("SearchDialog", "Hex"))
        self.cbFindFormat.setItemText(1, _translate("SearchDialog", "UTF-8"))
        self.gbReplace.setTitle(_translate("SearchDialog", "Replace"))
        self.cbReplaceFormat.setItemText(0, _translate("SearchDialog", "Hex"))
        self.cbReplaceFormat.setItemText(1, _translate("SearchDialog", "UTF-8"))
        self.gbOptions.setTitle(_translate("SearchDialog", "Options"))
        self.cbBackwards.setText(_translate("SearchDialog", "&Backwards"))
        self.cbPrompt.setText(_translate("SearchDialog", "&Prompt on replace"))
        self.pbFind.setText(_translate("SearchDialog", "&Find"))
        self.pbFind.setShortcut(_translate("SearchDialog", "F3"))
        self.pbReplace.setText(_translate("SearchDialog", "&Replace"))
        self.pbReplaceAll.setText(_translate("SearchDialog", "Replace &All"))
        self.pbCancel.setText(_translate("SearchDialog", "&Close"))
