import hou

class FireSpread():
        def __init__(self, nodeName, source, network, fireImport):
            super(FireSpread, self).__init__()

            self.nodeName = nodeName
            self.source = source
            self.network = network
            self.fireImport = fireImport

        def convertVDB(self):
            convertVDB = hou.node("/obj/" + self.fireImport).createNode("convertvdb")
            convertVDB.parm('group').set("@name=density @name=flame @name=temperature @name=vel.x @name=vel.y @name=vel.z")
            convertVDB.parm('conversion').set(1)

            # Get the post process node and set its input to the convertVDB node
            postProcess = hou.node("/obj/" + self.fireImport + "/post_process")
            convertVDB.setInput(0, postProcess)

            self.fileCache = hou.node("/obj/" + self.fireImport).createNode("filecache")
            self.fileCache.parm('filemethod').set(1)
            self.fileCache.setInput(0, convertVDB)

            # Layout the network
            hou.node("/obj/" + self.fireImport).layoutChildren()

