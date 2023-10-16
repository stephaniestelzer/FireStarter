import hou
from PySide2 import QtCore, QtUiTools, QtWidgets

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
        
        # Setup "Create Geometry" button
        self.ui.btn_create.clicked.connect(self.buttonClicked)

        # Set end frame
        self.ui.endFrame.returnPressed.connect(self.setEndframe)
        self.ui.endFrame.editingFinished.connect(self.setEndframe)

        # Set start frame
        self.ui.startFrame.returnPressed.connect(self.setStartframe)
        self.ui.startFrame.editingFinished.connect(self.setStartframe)

        # Set-up taper slider
        self.ui.taperSlider.valueChanged[int].connect(self.adjustTaper)

        # Steady-burn checkbox
        self.ui.burnCheckBox.toggled.connect(self.steadyBurnToggle)

        # Set-up height slider
        self.ui.heightSlider.valueChanged[int].connect(self.adjustHeight)

        # Set-up brightness slider
        self.ui.brightnessSlider.valueChanged[int].connect(self.adjustBrightness);

        self.startFrame = 1
        self.endFrame = 12

        
    def buttonClicked(self):
        # hou.hipFile.load(self.hip_file_path, suppress_save_prompt=True)

        network_name = "FireStarter"
        self.fireStarter = hou.node("/obj").createNode("geo")
        self.fireStarter.setName("FireStarter")

        # Create the torus and set up the animation
        self.sourceGeo = self.fireStarter.createNode("torus")
        self.sourceGeo.parm('radx').set(0.5)
        self.sourceGeo.parm('rady').set(0.25)

        # Create the first transformation
        self.transform1 = self.fireStarter.createNode("xform")
        self.transform1.parm('tx').set(-1.3)
        self.transform1.setInput(0, self.sourceGeo)

        self.transform2 = self.fireStarter.createNode("xform")
        self.transform2.parm('tx').set(1.3)
        self.transform2.setInput(0, self.sourceGeo)

        # Merge the geo
        self.merge = self.fireStarter.createNode('merge')
        self.merge.setInput(0, self.transform1)
        self.merge.setInput(1, self.sourceGeo)
        self.merge.setInput(2, self.transform2)

        # Add object noise using the mountain node
        self.attribNoise = self.fireStarter.createNode('attribnoise')
        self.attribNoise.setInput(0, self.merge)

        self.attribNoise.parm('usenoiseexpression').set(True)
        self.attribNoise.parm('offset').setExpression("$F / 15")
        self.attribNoise.parm('attribs').set("P")
        self.attribNoise.parm('displace').set(True)
        self.attribNoise.parm('noiserange').set(1)
        self.attribNoise.parm('amplitude').set(0.25)

        # Create trail node
        self.trail = self.fireStarter.createNode('trail')
        self.trail.setInput(0, self.attribNoise)
        self.trail.parm('result').set(3)
        self.trail.parm('velapproximation').set(1)

        # Create attribute wrangle
        self.attrWrangle = self.fireStarter.createNode('attribwrangle')
        self.attrWrangle.setInput(0, self.trail)
        self.attrWrangle.parm("snippet").set("@v = @v*5;")

        # Create pyrosource
        self.pyrosource = self.fireStarter.createNode('pyrosource')
        self.pyrosource.setInput(0, self.attrWrangle)
        self.pyrosource.parm('mode').set(0)
        self.pyrosource.parm('attributes').set(3)
        
        # Burn, Temperature, Density
        self.pyrosource.parm('attribute1').set(2)
        self.pyrosource.parm('attribute2').set(1)
        self.pyrosource.parm('attribute3').set(0)

        # Create attribute randomize
        self.attrRandomize1 = self.fireStarter.createNode('attribrandomize')
        self.attrRandomize1.setInput(0, self.pyrosource)
        self.attrRandomize1.parm('name').set("burn")

        self.attrRandomize2 = self.fireStarter.createNode('attribrandomize')
        self.attrRandomize2.setInput(0, self.attrRandomize1)
        self.attrRandomize2.parm('name').set("temperature")

        self.attrRandomize3 = self.fireStarter.createNode('attribrandomize')
        self.attrRandomize3.setInput(0, self.attrRandomize2)
        self.attrRandomize3.parm('name').set("density")

        # Create Volume Rasterize Attributes
        self.volumeRasterize = self.fireStarter.createNode('volumerasterizeattributes')
        self.volumeRasterize.setInput(0, self.attrRandomize3)
        self.volumeRasterize.parm('attributes').set("burn temperature density v")

        # Create Pyrosolver
        self.pyrosolver = self.fireStarter.createNode('pyrosolver')
        self.pyrosolver.setInput(0, self.volumeRasterize)

        self.pyrosolver.parm('numsources').set(5)

        self.pyrosolver.parm('source_volume5').set("burn")
        self.pyrosolver.parm('source_vfield5').set("divergence")

        # Sets duration
        self.pyrosolver.parm('srclimitframerange').set(True)

        # Set flame height / lifespan
        self.pyrosolver.parm('flames_lifespan').set(0.68)

        # Sets voxel size
        self.pyrosolver.parm('divsize').set(0.05)

        # Add velocity
        self.pyrosolver.parm('calcspeed').set(True)

        # Add density from flame
        self.pyrosolver.parm('soot_doemit').set(True)

        # Add temperature from flame
        self.pyrosolver.parm('temperature_doadd').set(True)

        # Adjust smoke on the pyrosolver
        self.pyrosolver.parm('s_densityscale').set(0.02)
        self.pyrosolver.parm('fi_int').set(25)

        # Set initial temperature scale
        self.pyrosolver.parm('source_vscale2').set(0.01)

        # Create Convertvdb
        self.convertvdb = self.fireStarter.createNode('convertvdb')
        self.convertvdb.setInput(0, self.pyrosolver)

        # Create Pyrobakevolume
        self.pyrobake = self.fireStarter.createNode('pyrobakevolume')
        self.pyrobake.setInput(0, self.convertvdb)
        self.pyrobake.parm('enablefire').set(True)
        self.pyrobake.parm('kfire').set(1)

        # Set up smoke
        self.pyrobake.parm('firecolorramp1pos').set(0.0166945)
        self.pyrobake.parm('firecolorramp1cr').set(0.001)
        self.pyrobake.parm('firecolorramp1cg').set(0.001)
        self.pyrobake.parm('firecolorramp1cb').set(0.001)
        self.pyrobake.parm('densityscale').set(0.02)


        # Create output
        self.output = self.fireStarter.createNode('output')
        self.output.setInput(0, self.pyrobake)

        # Layout all nodes in the network
        self.fireStarter.layoutChildren()

        # Set parm to steady burn at first
        self.pyrosolver.parm('srclimitframerange').set(False)

    def adjustTaper(self):
        print("hello world")

    def adjustBrightness(self):
        value = (self.ui.brightnessSlider.value() / 100.0)
        brightness = value * (4950 / 49)

        if brightness == 0:
            self.pyrobake.parm('kfire').set(1)
        else:
            self.pyrobake.parm('kfire').set(brightness)

        print(brightness)
    
    def adjustHeight(self):
        value = self.ui.heightSlider.value()

        # Multiply the slider by the ratio to get the Temperature Scale value
        tempValue = value * (169/9900)

        # Account for edge cases
        if value == 0:
            tempValue = 0.01
        if value == 99:
            tempValue = 1.7

        self.pyrosolver.parm('source_vscale2').set(tempValue)

    def setEndframe(self):
        # If steady burn is checked... do nothing
        if self.ui.burnCheckBox.isChecked():
            print("Steady burn is checked -- unable to set frame range")
            return
        else:
            # Check for a valid input
            input = self.ui.endFrame.text()
            try:
                self.endFrame = int(input)
                self.pyrosolver.parm('srcframerangemax').set(self.endFrame)
            except ValueError:
                self.ui.endFrame.setText(str(self.endFrame))

    def setStartframe(self):
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
        if self.ui.burnCheckBox.isChecked():
            # Don't limit the frame range
            self.pyrosolver.parm('srclimitframerange').set(False)
            self.ui.startFrame.setText("")
            self.ui.endFrame.setText("")

        else: 
            self.pyrosolver.parm('srclimitframerange').set(True)
            # Set start and end frames
            self.pyrosolver.parm('srcframerangemin').set(self.startFrame)
            self.pyrosolver.parm('srcframerangemax').set(self.endFrame)
            # Set the frame range to the previous number of frames
            self.ui.startFrame.setText(str(self.startFrame))
            self.ui.endFrame.setText(str(self.endFrame))
        

def run():
    win = FireStarter()
    win.show()
