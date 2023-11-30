import hou
import dopsparsepyrotools
from PySide2 import QtCore, QtUiTools, QtWidgets, QtGui
from PySide2.QtGui import QColor

from Campfire import Campfire
from FireSpread import FireSpread

class customItemWidget(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()

        self.nodeName = name

        self.label = QtWidgets.QLabel(name)
        self.button = QtWidgets.QPushButton("Export")
        self.button.clicked.connect(self.exportSim)
        layout = QtWidgets.QGridLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.button, 0, 1)

    def sizeHint(self):
        return self.minimumSizeHint()
    
    def exportSim(self):
        print("connected")
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ShowDirsOnly  # Set the option to show only directories

        # Set the initial directory to your specified folder
        folderPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", "/", options=options)
        
        if (self.nodeName.startswith("Campfire")):
            print("Campfire")
            # Access this node's fileCache
            if(folderPath):
                print(folderPath)
        else:
            print("FireSpread")
            if(folderPath):
                print(folderPath)
                # Get access to the fire import's file cache node
                fileCache = hou.node("/obj/" + self.nodeName + "/filecache1")
                fileCache.parm('file').set(folderPath + "/$F.vdb")
                fileCache.parm('execute').pressButton()


class FireStarter(QtWidgets.QWidget):
    def __init__(self):
        if hasattr(self, 'ui'):
            return
        
        super(FireStarter, self).__init__()
        ui_file = '/Users/stephaniestelzer/Documents/HoudiniPlugins/FireStarter/SmallerUI.ui'
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

        # Set-up color picker
        self.ui.colorChoose.clicked.connect(self.changeFireColor)

        # Initialize stacked widget & add the dropdown
        self.ui.stackedWidget.setCurrentIndex(0)

        self.startFrame = 1
        self.endFrame = 12
        
        ## ---------- SPREAD UI SET-UP ------------------------- #
        self.ui.openFile.clicked.connect(self.openFile)
        self.ui.createFireSpread.clicked.connect(self.createFireSim)

        # Initialize number of simulations
        self.simNumber = 0
        self.spreadNumber = 0

        self.campfireDict = {}
        self.spreadDict = {}

    def detectDeletion(self):
        print("Deletion Detected")

    def findChildNode(self, nodeName):
        # Start at object level
        obj = hou.node("/obj/")
        currentNode = obj

        while currentNode:
            enclosingNetwork = currentNode.parent()
            print("Enclosing Network: " + enclosingNetwork.name())
            if enclosingNetwork and enclosingNetwork.type().name() == enclosingNetwork:
                # Search nodes within the network
                foundNode = enclosingNetwork.node(nodeName)
                if (foundNode):
                    return foundNode
            currentNode = enclosingNetwork
        
        return None

    
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
            
    def enableSpreadMenu(self):
        print("Not Accessible Yet")

    def disableSpreadMenu(self):
        print("Not Accessible Yet")


    def selectionChangedCallback(self):
        print("Selection")

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

        # Rename the created nodes to the proper name space so that they can be accessed
        # sourceNode = self.findChildNode(nodeName)

        sourceName = hou.node("/obj/" + nodeName + "_source")
        print(nodes[0].path())
        newSourceName = nodeName + "_source" + str(self.spreadNumber)
        sourceName.setName(newSourceName) # This is the line that causes error when using with an imported file

        fireSim = hou.node("/obj/fire_simulation")
        newFireSim = "fire_simulation" + str(self.spreadNumber)
        fireSim.setName(newFireSim)

        fireImport = hou.node("/obj/fire_import")
        newFireImport = "fire_import" + str(self.spreadNumber)
        fireImport.setName(newFireImport)

        # Create a new FireSpread object and add it to the map
        self.spreadNumber += 1
        fireSpread = FireSpread(nodeName, newSourceName, newFireSim, newFireImport)
        fireSpread.convertVDB()

        self.spreadDict[nodeName] = fireSpread

        # Add a new item to export list
                # Add the simulation to the layout
        newItem = QtWidgets.QListWidgetItem(self.ui.exportList)
        custom = customItemWidget(newFireImport)
        newItem.setSizeHint(custom.sizeHint())
        self.ui.exportList.setItemWidget(newItem, custom)

def run():        
    win = FireStarter()
    win.show()
