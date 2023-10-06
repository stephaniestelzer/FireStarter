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
        self

        # Simulation Path
        self.hip_file_path = "/Users/stephaniestelzer/Desktop/Basic_Simulation.hipnc"
        
    def buttonClicked(self):
        # customName = "campfire"
        # print("accessed")
        
        # hou.hipFile.load(self.hip_file_path, suppress_save_prompt=True)  # Fix typo here

        # network_name = "FireStarter"
        # geometry_network = hou.node("/obj").node(network_name)

        # # Create a copy of the network in the current scene
        # new_object = hou.node("/obj").createNode("geo", "Fire_Starter")
        # geometry_network.copyItemsTo(new_object)
        hou.hipFile.load(self.hip_file_path, suppress_save_prompt=True)

        network_name = "FireStarter"
        geometry_network = hou.node("/obj").node(network_name)
      
    def checkExisting(self, geometryName):
        # Check if the specified node exists
        if hou.node('/obj/{}'.format(geometryName)):
            # Display fail message
            hou.ui.displayMessage('{} already exists in the scene'.format(geometryName))
            return True
        return False  # Return False if the node doesn't exist

    def createGeoNode(self, geometryName):
        # Get scene root node
        sceneRoot = hou.node('/obj/')
        
        # Create a subnet node (change 'subnet' to 'geo' if you want a geometry node)
        geo_subnet = sceneRoot.createNode('subnet')
        
        # Set subnet node name
        geo_subnet.setName(geometryName)
        
        # Display creation message
        hou.ui.displayMessage('{} node created!'.format(geometryName))

def run():
    win = FireStarter()
    win.show()
