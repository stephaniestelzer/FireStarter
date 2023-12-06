import hou

class FireSpread():
        def __init__(self, nodeName, source, network, fireImport):
            super(FireSpread, self).__init__()

            self.nodeName = nodeName
            self.source = source
            self.network = network
            self.fireImport = fireImport

        def convertVDB(self):
            convertVDB = self.fireImport.createNode("convertvdb")
            convertVDB.parm('group').set("@name=density @name=flame @name=temperature @name=vel.x @name=vel.y @name=vel.z")
            convertVDB.parm('conversion').set(1)

            # Get the post process node and set its input to the convertVDB node
            postProcess = hou.node(self.fireImport.path() + "/post_process")
            convertVDB.setInput(0, postProcess)

            self.fileCache = self.fireImport.createNode("filecache")
            self.fileCache.parm('filemethod').set(1)
            self.fileCache.setInput(0, convertVDB)

            # Layout the network
            self.fireImport.layoutChildren()

        def setSpeed(self, speed):
            print(self.source.path() + "/simulate_spread")
            spreadNode = hou.node(self.source.path() + "/simulate_spread")
            spreadNode.parm('diff_rate').set(speed)
            
        def setStartFrame(self, frame):
            print(self.source.path() + "/simulate_spread")
            spreadNode = hou.node(self.source.path() + "/simulate_spread")
            spreadNode.parm('startframe').set(frame)
