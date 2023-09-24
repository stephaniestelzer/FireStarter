import hou
from PySide2 import QtCore, QtUiTools, QtWidgets

class GeoCreator(QtWidgets.QWidget):
    def __init__(self):
        super(GeoCreator, self).__init__()
        ui_file = '/Users/stephaniestelzer/Documents/HoudiniPlugins/FireStarter/StarterUI.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        
        # Setup "Create Geometry" button
        self.ui.btn_create.clicked.connect(self.buttonClicked)
        
    def buttonClicked(self):
        customName = self.ui.lin_name.text()
        
        # Execute node creation 
        if not self.checkExisting(customName):
            self.createGeoNode(customName)
    
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
    win = GeoCreator()
    win.show()
