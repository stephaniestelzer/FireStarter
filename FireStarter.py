import hou
from PySide2 import QtCore, QtUiTools, QtWidgets

class FireStarter(QtWidgets.QWidget):
    def __init__(self):
        super(FireStarter, self).__init__()
        ui_file = '/Users/stephaniestelzer/Documents/HoudiniPlugins/FireStarter/SmallerUI.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        
        # Setup "Create Geometry" button
        self.ui.btn_create.clicked.connect(self.buttonClicked)
        # Set number of frames when a user presses enter or clicks out of the box
        self.ui.durationInput.returnPressed.connect(self.setDuration)
        self.ui.durationInput.editingFinished.connect(self.setDuration)

        # Set-up taper slider
        self.ui.taperSlider.valueChanged[int].connect(self.adjustTaper)
        self.ui.burnCheckBox.toggled.connect(self.steadyBurnToggle)

        self.numFrames = 12

        
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
        self.attribNoise.parm('offset').set(hou.frame()/15)
        # self.attribNoise.parm('attribtype').set(['P']) Have to manually set P for now
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
        # self.pyrosolver.parm('solver').set(2)

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

        # Set it initially to steady burn
        self.pyrosolver.parm('srclimitframerange').set(False)

        # Create Convertvdb
        self.convertvdb = self.fireStarter.createNode('convertvdb')
        self.convertvdb.setInput(0, self.pyrosolver)

        # Create Pyrobakevolume
        self.pyrobake = self.fireStarter.createNode('pyrobakevolume')
        self.pyrobake.setInput(0, self.convertvdb)
        self.pyrobake.parm('enablefire').set(True)

        # Create output
        self.output = self.fireStarter.createNode('output')
        self.output.setInput(0, self.pyrobake)

        # Layout all nodes in the network
        self.fireStarter.layoutChildren()

        # Set parm to steady burn at first
        self.pyrosolver.parm('srclimitframerange').set(False)


    def adjustTaper(self):
        print("hello world")

    def setDuration(self):
        # If steady burn is checked... do nothing
        if self.ui.burnCheckBox.isChecked():
            print("Steady burn is checked -- unable to set frame range")
            return
        else:
            # Check for a valid input
            input = self.ui.durationInput.text()
            try:
                self.numFrames = int(input)
                self.pyrosolver.parm('srcframerangemax').set(self.numFrames)
            except ValueError:
                self.ui.durationInput.setText(str(self.numFrames))





    
    def steadyBurnToggle(self):
        if self.ui.burnCheckBox.isChecked():
            # Don't limit the frame range
            self.pyrosolver.parm('srclimitframerange').set(False)
            self.ui.durationInput.setText("")

        else: 
            self.pyrosolver.parm('srclimitframerange').set(True)
            # Set the maximum frames based
            self.pyrosolver.parm('srcframerangemax').set(self.numFrames)
            if not self.ui.durationInput.text().strip():
                # Set the frame range to the previous number of frames
                self.ui.durationInput.setText(str(self.numFrames))
        

def run():
    win = FireStarter()
    win.show()
