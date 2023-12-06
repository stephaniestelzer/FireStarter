import os
import hou
import dopsparsepyrotools
from PySide2 import QtCore, QtUiTools, QtWidgets, QtGui
from PySide2.QtGui import QColor

from Campfire import Campfire
from FireSpread import FireSpread

class customItemWidget(QtWidgets.QWidget):
    def __init__(self, path):
        super().__init__()

        self.nodePath = path

        self.label = QtWidgets.QLabel(path)
        self.button = QtWidgets.QPushButton("Export")
        self.button.clicked.connect(self.exportSim)
        layout = QtWidgets.QGridLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.button, 0, 1)

    def sizeHint(self):
        return self.minimumSizeHint()
    
    def exportSim(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ShowDirsOnly  # Set the option to show only directories

        # Set the initial directory to your specified folder
        folderPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", "/", options=options)
        
        nodeStringSplit = self.nodePath.split("/")
        rootName = '/'.join(nodeStringSplit[:-1])

        if (self.nodePath.startswith("Campfire")):
            # Access this node's fileCache
            if(folderPath):
                # Get access to the fire import's file cache node
                print(folderPath)
                fileCache = hou.node("/obj/" + self.nodePath + "/filecache1")
                fileCache.parm('file').set(folderPath + "/$F.vdb")
                fileCache.parm('execute').pressButton()
        else:
            if(folderPath):
                print(folderPath)
                # Get access to the fire import's file cache node
                fileCache = hou.node(self.nodePath + "/filecache1")
                fileCache.parm('file').set(folderPath + "/$F.vdb")
                fileCache.parm('execute').pressButton()


class FireStarter(QtWidgets.QWidget):
    def __init__(self):
        if hasattr(self, 'ui'):
            return
        
        super(FireStarter, self).__init__()
        cdir = os.getcwd() 
        #V print("Current Directory: ", cdir) 
        path = os.path.abspath(__file__).split("/")
        rootName = '/'.join(path[:-1])

        ui_file = rootName + '/SmallerUI.ui'
        print("Root File: " + rootName)
        print("UI File: " + ui_file)
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        # Set the 'always on top' flag
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

        # Add event listener
        # hou.session.myEventHandler = hou.ui.addEventCallback(hou.nodeEventType.BeingDeleted, self.detectDeletion())
        
        ## ---------- CAMPFIRE UI SET-UP -------------------- #
        # Setup "Create Geometry" button
        self.ui.btn_create.clicked.connect(self.buttonClicked)

        # Set end frame
        self.ui.endFrame.returnPressed.connect(self.setEndframe)
        self.ui.endFrame.editingFinished.connect(self.setEndframe)

        # Set start frame
        self.ui.startFrame.returnPressed.connect(self.setStartframe)
        self.ui.startFrame.editingFinished.connect(self.setStartframe)

        # Set-up taper slider
        self.ui.compactnessSlider.valueChanged[int].connect(self.adjustCompactness)

        # Steady-burn checkbox
        self.ui.burnCheckBox.toggled.connect(self.steadyBurnToggle)

        # Set-up height slider
        self.ui.heightSlider.valueChanged[int].connect(self.adjustHeight)

        # Set-up brightness slider
        self.ui.brightnessSlider.valueChanged[int].connect(self.adjustBrightness)

        # Set-up Dropdown
        self.ui.simulationType.addItems(['Campfire', 'Spread', 'Export'])
        self.ui.simulationType.currentIndexChanged.connect(self.changeUI)

        # Get path of current directory
        script_directory = os.path.dirname(os.path.abspath(__file__))

        self.colorIcon = QtGui.QIcon(rootName + "/images/icon-color-smart.png")
        self.ui.colorChoose.setIconSize(QtCore.QSize(64, 64))
        self.ui.colorChoose.setIcon(self.colorIcon)

        # Set-up color picker
        self.ui.colorChoose.clicked.connect(self.changeFireColor)

        # Initialize stacked widget & add the dropdown
        self.ui.stackedWidget.setCurrentIndex(0)

        self.startFrame = 1
        self.endFrame = 12
        
        ## ---------- SPREAD UI SET-UP ------------------------- #
        self.ui.openFile.clicked.connect(self.openFile)
        self.ui.createFireSpread.clicked.connect(self.createFireSim)

        self.ui.spreadSpeed.valueChanged[int].connect(self.setSpreadSpeed)

        self.ui.spreadStart.returnPressed.connect(self.spreadStartFrame)
        self.ui.spreadStart.editingFinished.connect(self.spreadStartFrame)

        # Initialize number of simulations
        self.simNumber = 0
        self.spreadNumber = 0

        self.campfireDict = {}
        self.spreadDict = {}

    def detectDeletion(self):
        print("Deletion Detected")

    def setSpreadSpeed(self):
        # get the spread node
        value = (self.ui.spreadSpeed.value() / 10.0)
        value += 1
        i = self.getSpreadNode()
        i.setSpeed(value)

    def spreadStartFrame(self):
        input = self.ui.spreadStart.text()
        i = self.getSpreadNode()
        i.setStartFrame(int(input))
    
    def enableCampfireMenu(self):
        campfirePage = self.ui.stackedWidget.widget(0)
        for widget in campfirePage.findChildren(QtWidgets.QWidget):
            widget.setEnabled(True)

    def disableCampfireMenu(self):
        excludedName = ['btn_create']
        campfirePage = self.ui.stackedWidget.widget(0)
        for widget in campfirePage.findChildren(QtWidgets.QWidget):
            print(widget.objectName())
            if str(widget.objectName()) not in excludedName:
                print("Accessed")
                widget.setEnabled(False)

    def openFile(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "USD Files (*.USD);;FBX Files (*.fbx);;OBJ Files (*.obj)", options=options)

        if file_path:
            # Do something with the selected file (e.g., load or process it)
            fileExtension = file_path.split(".")[-1]
            if fileExtension == "fbx":
                hou.hipFile.importFBX(file_path)
            if fileExtension == "usd":
                # Create a geometry node to house the USD import
                objNetwork = hou.node("/obj")
                # Have to account for if the geo node has been created here
                geomNode = objNetwork.createNode("geo", "USD_ImportedGeo")
                # Create USD Import node
                usdImportNode = geomNode.createNode("usdimport")
                usdImportNode.parm("filepath1").set(file_path)

    def changeUI(self):
        page = self.ui.simulationType.currentText()
        if page == "Export":
            self.ui.stackedWidget.setCurrentIndex(2)
        if page == "Spread":
            self.ui.stackedWidget.setCurrentIndex(1)
        if page == "Campfire":
            self.ui.stackedWidget.setCurrentIndex(0)

    def buttonClicked(self):
        self.simNumber += 1
        campfire = Campfire(self.simNumber)
        networkName = "Campfire_" + str(self.simNumber)
        self.campfireDict[networkName] = campfire

        # Add the simulation to the list
        newItem = QtWidgets.QListWidgetItem(self.ui.exportList)
        custom = customItemWidget(networkName)
        newItem.setSizeHint(custom.sizeHint())
        self.ui.exportList.setItemWidget(newItem, custom)

    def getCampfireNode(self):
        nodes = hou.selectedNodes()
        if len(nodes) != 1:
            return None
        
        nodeName = nodes[0].name()
        campfireNode = self.campfireDict[nodeName]
        return campfireNode

    def getSpreadNode(self):
        nodes = hou.selectedNodes()
        if len(nodes) != 1:
            return None
        
        nodeName = nodes[0].name()
        spreadNode = self.spreadDict[nodeName]
        return spreadNode

    def adjustCompactness(self):
        value = (self.ui.compactnessSlider.value() / 10.0)
        i = self.getCampfireNode()
        if i != None:
            if value == 0:
                i.pyrosolver.parm('enable_viscosity').set(False)
            else:
                i.pyrosolver.parm('enable_viscosity').set(True)
                i.pyrosolver.parm('viscosity').set(value / 10)


    def adjustBrightness(self):
        n = self.getCampfireNode()
        if (n != None):
            value = (self.ui.brightnessSlider.value() / 100.0)
            brightness = value * (4950 / 49)

            if brightness == 0:
                n.pyrobake.parm('kfire').set(1)
            else:
                n.pyrobake.parm('kfire').set(brightness)

            print(brightness)
    
    def adjustHeight(self):
        n = self.getCampfireNode()
        if n != None:
            value = self.ui.heightSlider.value()

            # Multiply the slider by the ratio to get the Temperature Scale value
            tempValue = value * (169/9900)

            # Account for edge cases
            if value == 0:
                tempValue = 0.01
            if value == 99:
                tempValue = 1.7

            n.pyrosolver.parm('source_vscale2').set(tempValue)

    def setEndframe(self):
        n = self.getCampfireNode()
        # If steady burn is checked... do nothing
        if n != None:
            if self.ui.burnCheckBox.isChecked():
                print("Steady burn is checked -- unable to set frame range")
                return
            else:
                # Check for a valid input
                input = self.ui.endFrame.text()
                try:
                    self.endFrame = int(input)
                    n.pyrosolver.parm('srcframerangemax').set(self.endFrame)
                except ValueError:
                    self.ui.endFrame.setText(str(self.endFrame))

    def setStartframe(self):
        n = self.getCampfireNode()
        if n != None:
            # If steady burn is checked... do nothing
            if self.ui.burnCheckBox.isChecked():
                print("Steady burn is checked -- unable to set frame range")
                return
            else:
                # Check for a valid input
                input = self.ui.startFrame.text()
                try:
                    self.startFrame = int(input)
                    self.pyrosolver.parm('srcframerangemin').set(self.startFrame)
                except ValueError:
                    self.ui.startFrame.setText(str(self.startFrame))


    def steadyBurnToggle(self):
        n = self.getCampfireNode()
        if n != None:
            if self.ui.burnCheckBox.isChecked():
                # Don't limit the frame range
                n.pyrosolver.parm('srclimitframerange').set(False)
                self.ui.startFrame.setText("")
                self.ui.endFrame.setText("")

            else: 
                n.pyrosolver.parm('srclimitframerange').set(True)
                # Set start and end frames
                n.pyrosolver.parm('srcframerangemin').set(self.startFrame)
                n.pyrosolver.parm('srcframerangemax').set(self.endFrame)
                # Set the frame range to the previous number of frames
                self.ui.startFrame.setText(str(self.startFrame))
                self.ui.endFrame.setText(str(self.endFrame))

    def changeFireColor(self):
        print("Accessed")
        n = self.getCampfireNode()
        if n != None:
            color = QtWidgets.QColorDialog().getColor()
            if color.isValid():
                # Returns hex code of selected color
                hexColor = color.name().lstrip("#")
                print(hexColor)
                rgb = tuple(int(hexColor[i:i+2], 16) for i in (0, 2, 4))
                print(rgb)
                n.pyrobake.parm('firecolorramp2cr').set( (rgb[0]) / 255)
                n.pyrobake.parm('firecolorramp2cg').set( (rgb[1]) / 255)
                n.pyrobake.parm('firecolorramp2cb').set( (rgb[2]) / 255)

    def createFireSim(self, kwargs):
        # Get the name of the node before creating the new nodes
        nodes = hou.selectedNodes()
        if len(nodes) != 1:
            return None
        
        nodeName = nodes[0].name()

        # Use the 'Fire Spread' shelf button
        dopsparsepyrotools.createSpreadingFire(kwargs = {})

        sourceName = hou.node(nodes[0].path() + "_source")
        print("Source Name: " + sourceName.path())
        newSourceName = nodeName + "_source" + str(self.spreadNumber)
        sourceName.setName(newSourceName) # This is the line that causes error when using with an imported file

        # Splitting the selected node path for parsing
        nodePath = nodes[0].path()
        pathSplit = nodePath.split("/")
        hiearchyString = '/'.join(pathSplit[:-1])

        # Hierarchy string now contains the parent network of the node
        fireSim = hou.node(hiearchyString + "/fire_simulation")
        newFireSim = "fire_simulation" + str(self.spreadNumber)
        fireSim.setName(newFireSim)

        fireImport = hou.node(hiearchyString + "/fire_import")
        newFireImport = "fire_import" + str(self.spreadNumber)
        fireImport.setName(newFireImport)

        # Create a new FireSpread object and add it to the map
        self.spreadNumber += 1
        fireSpread = FireSpread(nodeName, sourceName, fireSim, fireImport)
        fireSpread.convertVDB()

        self.spreadDict[nodeName] = fireSpread

        # Add a new item to export list
        newItem = QtWidgets.QListWidgetItem(self.ui.exportList)
        custom = customItemWidget(fireImport.path())
        newItem.setSizeHint(custom.sizeHint())
        self.ui.exportList.setItemWidget(newItem, custom)

def run():        
    win = FireStarter()
    win.show()
