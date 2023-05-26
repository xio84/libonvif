#*******************************************************************************
# onvif-gui/gui/components/directoryselector.py
#
# Copyright (c) 2023 Stephen Rhodes 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#******************************************************************************/

from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, \
    QLabel, QGridLayout, QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject

class DirectorySelectorSignals(QObject):
    dirChanged = pyqtSignal(str)

class DirectorySelector(QWidget):
    def __init__(self, mw, name, label, location=""):
        super().__init__()
        self.mw = mw
        self.directoryKey = name + "/directory"
        self.signals = DirectorySelectorSignals()

        self.txtDirectory = QLineEdit()
        self.txtDirectory.setText(self.mw.settings.value(self.directoryKey, location))
        self.txtDirectory.textEdited.connect(self.txtDirectoryChanged)
        self.btnSelect = QPushButton("...")
        self.btnSelect.clicked.connect(self.btnSelectClicked)
        lblSelect = QLabel(label)

        lytMain = QGridLayout(self)
        lytMain.setContentsMargins(0, 0, 0, 0)
        lytMain.addWidget(lblSelect,           0, 0, 1, 1)
        lytMain.addWidget(self.txtDirectory,   0, 1, 1, 1)
        lytMain.addWidget(self.btnSelect,      0, 2, 1, 1)
        lytMain.setColumnStretch(1, 10)
        self.setContentsMargins(0, 0, 0, 0)

    def btnSelectClicked(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory", self.txtDirectory.text())
        
        if len(path) > 0:
            self.txtDirectory.setText(path)
            self.txtDirectoryChanged(path)

    def txtDirectoryChanged(self, text):
        self.mw.settings.setValue(self.directoryKey, text)
        self.signals.dirChanged.emit(text)

    def text(self):
        return self.txtDirectory.text()

