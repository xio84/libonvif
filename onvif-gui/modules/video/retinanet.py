#/********************************************************************
#libonvif/gui/modules/video/retinanet.py 
#
# Copyright (c) 2023  Stephen Rhodes
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
#*********************************************************************/

IMPORT_ERROR = ""
try:
    import cv2
    import numpy as np
    from loguru import logger
    from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QMessageBox
    from PyQt5.QtCore import Qt
    from gui.components.thresholdslider import ThresholdSlider
    from gui.components.labelselector import LabelSelector

    import torch
    import torchvision
    import torchvision.transforms as transforms

    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
except ModuleNotFoundError as ex:
    IMPORT_ERROR = str(ex)
    print("Import Error has occurred, missing modules need to be installed, please consult documentation: ", ex)

MODULE_NAME = "retinanet"

class VideoConfigure(QWidget):
    def __init__(self, mw):
        try:
            super().__init__()
            self.mw = mw
            self.name = MODULE_NAME

            self.sldThreshold = ThresholdSlider(mw, MODULE_NAME, "Confidence", 35)
            
            number_of_labels = 5
            self.labels = []
            for i in range(number_of_labels):
                self.labels.append(LabelSelector(mw, MODULE_NAME, i+1))

            pnlLabels = QWidget()
            lytLabels = QGridLayout(pnlLabels)
            lblPanel = QLabel("Select classes to be indentified")
            lblPanel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lytLabels.addWidget(lblPanel,        0, 0, 1, 1)
            for i in range(number_of_labels):
                lytLabels.addWidget(self.labels[i], i+1, 0, 1, 1)
            lytLabels.setContentsMargins(0, 0, 0, 0)

            lytMain = QGridLayout(self)
            lytMain.addWidget(self.sldThreshold,        0, 0, 1, 1)
            lytMain.addWidget(pnlLabels,                1, 0, 1, 1)
            lytMain.addWidget(QLabel(""),               2, 0, 1, 1)
            lytMain.setRowStretch(2, 10)

            if len(IMPORT_ERROR) > 0:
                QMessageBox.critical(None, "Retinanet Import Error", "Modules required for running this function are missing: " + IMPORT_ERROR)

        except:
            logger.exception("retinanet configuration load error")

class VideoWorker:
    def __init__(self, mw):
        try:
            self.mw = mw
            self.last_ex = ""
            self.model = torchvision.models.detection.retinanet_resnet50_fpn(weights=torchvision.models.detection.RetinaNet_ResNet50_FPN_Weights.DEFAULT)            
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.eval().to(self.device)
        except:
            logger.exception("retinanet worker load error")

    def __call__(self, F):
        try:
            img = np.array(F, copy = False)
            tensor = transform(img).to(self.device)
            tensor = tensor.unsqueeze(0)

            with torch.no_grad():
                outputs = self.model(tensor)

            threshold = self.mw.configure.sldThreshold.value()
            scores = outputs[0]['scores'].detach().cpu().numpy()
            labels = outputs[0]['labels'].detach().cpu().numpy()
            boxes = outputs[0]['boxes'].detach().cpu().numpy()

            labels = labels[np.array(scores) >= threshold]
            boxes = boxes[np.array(scores) >= threshold].astype(np.int32)
            for lbl in self.mw.configure.labels:
                if lbl.chkBox.isChecked():
                    label = lbl.cmbLabel.currentIndex() + 1
                    lbl_boxes = boxes[np.array(labels) == label]
                    r = lbl.color()[0]
                    g = lbl.color()[1]
                    b = lbl.color()[2]
                    lbl.setCount(lbl_boxes.shape[0])

                    for box in lbl_boxes:
                        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (r, g, b), 2)

        except Exception as ex:
            if self.last_ex != str(ex) and self.mw.configure.name == MODULE_NAME:
                logger.exception("retinanet worker call error")
            self.last_ex = str(ex)

