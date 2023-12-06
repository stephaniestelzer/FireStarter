import hou

class Campfire():
        def __init__(self, num):
            super(Campfire, self).__init__()
            
            self.networkName = "Campfire_" + str(num)
            self.campfire = hou.node("/obj").createNode("geo")
            self.campfire.setName(self.networkName)

            # Create the torus and set up the animation
            self.sourceGeo = self.campfire.createNode("torus")
            self.sourceGeo.parm('radx').set(0.5)
            self.sourceGeo.parm('rady').set(0.25)

            # Create the first transformation
            self.transform1 = self.campfire.createNode("xform")
            self.transform1.parm('tx').set(-1.3)
            self.transform1.setInput(0, self.sourceGeo)

            self.transform2 = self.campfire.createNode("xform")
            self.transform2.parm('tx').set(1.3)
            self.transform2.setInput(0, self.sourceGeo)

            # Merge the geo
            self.merge = self.campfire.createNode('merge')
            self.merge.setInput(0, self.transform1)
            self.merge.setInput(1, self.sourceGeo)
            self.merge.setInput(2, self.transform2)

            # Add object noise using the mountain node
            self.attribNoise = self.campfire.createNode('attribnoise')
            self.attribNoise.setInput(0, self.merge)

            self.attribNoise.parm('usenoiseexpression').set(True)
            self.attribNoise.parm('offset').setExpression("$F / 15")
            self.attribNoise.parm('attribs').set("P")
            self.attribNoise.parm('displace').set(True)
            self.attribNoise.parm('noiserange').set(1)
            self.attribNoise.parm('amplitude').set(0.25)

            # Create trail node
            self.trail = self.campfire.createNode('trail')
            self.trail.setInput(0, self.attribNoise)
            self.trail.parm('result').set(3)
            self.trail.parm('velapproximation').set(1)

            # Create attribute wrangle
            self.attrWrangle = self.campfire.createNode('attribwrangle')
            self.attrWrangle.setInput(0, self.trail)
            self.attrWrangle.parm("snippet").set("@v = @v*5;")

            # Create pyrosource
            self.pyrosource = self.campfire.createNode('pyrosource')
            self.pyrosource.setInput(0, self.attrWrangle)
            self.pyrosource.parm('mode').set(0)
            self.pyrosource.parm('attributes').set(3)
            
            # Burn, Temperature, Density
            self.pyrosource.parm('attribute1').set(2)
            self.pyrosource.parm('attribute2').set(1)
            self.pyrosource.parm('attribute3').set(0)

            # Create attribute randomize
            self.attrRandomize1 = self.campfire.createNode('attribrandomize')
            self.attrRandomize1.setInput(0, self.pyrosource)
            self.attrRandomize1.parm('name').set("burn")

            self.attrRandomize2 = self.campfire.createNode('attribrandomize')
            self.attrRandomize2.setInput(0, self.attrRandomize1)
            self.attrRandomize2.parm('name').set("temperature")

            self.attrRandomize3 = self.campfire.createNode('attribrandomize')
            self.attrRandomize3.setInput(0, self.attrRandomize2)
            self.attrRandomize3.parm('name').set("density")

            # Create Volume Rasterize Attributes
            self.volumeRasterize = self.campfire.createNode('volumerasterizeattributes')
            self.volumeRasterize.setInput(0, self.attrRandomize3)
            self.volumeRasterize.parm('attributes').set("burn temperature density v")

            # Create Pyrosolver
            self.pyrosolver = self.campfire.createNode('pyrosolver')
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

            # Create Pyrobakevolume
            self.pyrobake = self.campfire.createNode('pyrobakevolume')
            self.pyrobake.setInput(0, self.pyrosolver)
            self.pyrobake.parm('enablefire').set(True)
            self.pyrobake.parm('kfire').set(1)

            # Set up smoke
            self.pyrobake.parm('firecolorramp1pos').set(0.0166945)
            self.pyrobake.parm('firecolorramp1cr').set(0.001)
            self.pyrobake.parm('firecolorramp1cg').set(0.001)
            self.pyrobake.parm('firecolorramp1cb').set(0.001)
            self.pyrobake.parm('densityscale').set(0.02)

            # Change the bindings to match the pyrosolver -- this still isn't getting the color to show up in Maya
            self.pyrobake.parm('firek_volumename').set("flame")
            self.pyrobake.parm('firecolor_volumename').set("flame")
            self.pyrobake.setDisplayFlag(True)

            # Create Convertvdb
            self.convertvdb = self.campfire.createNode('convertvdb')
            self.convertvdb.setInput(0, self.pyrobake)
            self.convertvdb.parm('group').set("@name=density @name=flame @name=temperature @name=vel.x @name=vel.y @name=vel.z")
            self.convertvdb.parm('conversion').set(1)

            # Create filecache
            self.fileCache = self.campfire.createNode("filecache")
            self.fileCache.parm('filemethod').set(1)
            self.fileCache.setInput(0, self.convertvdb)

            # Layout all nodes in the network
            self.campfire.layoutChildren()

            # Set parm to steady burn at first
            self.pyrosolver.parm('srclimitframerange').set(False)
