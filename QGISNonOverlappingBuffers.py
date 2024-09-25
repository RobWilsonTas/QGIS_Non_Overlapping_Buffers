import datetime
from pathlib import Path
startTime = datetime.time()


"""
##########################################################
User options for the tiling section
"""

#Initial variable assignment
polygonLayer1 = 'D:/Other Tasks/BigMapV4/PrivateLandSpatialData/TestClipoutPublic.gpkg' #E.g 'C:/Temp/BigImage.tif'
polygonLayer2 = 'D:/Other Tasks/BigMapV4/PrivateLandSpatialData/TestClipoutPrivate.gpkg' #

maximumGap = 200
errorTolerance = 2


"""
#######################################################################
#######################################################################
"""

#Set up the layer name for the raster calculations
inImageName = polygonLayer1.split("/")
inImageName = inImageName[-1]
inImageName = inImageName[:len(inImageName)-4]
outImageName = inImageName

#Making a folder for processing
rootProcessDirectory = str(Path(polygonLayer1).parent.absolute()).replace('\\','/') + '/'
processDirectory = rootProcessDirectory + 'ProcessBuffer' + '/'
if not os.path.exists(processDirectory): os.mkdir(processDirectory)


"""
##########################################################
Looped processing
"""


currentBuffDistance = maximumGap / 2
currentSimpFactor = errorTolerance * 0.95

currentBasePolygonLayer1 = polygonLayer1
currentBasePolygonLayer2 = polygonLayer2


while currentBuffDistance > (errorTolerance/8):
    
    processing.run("native:buffer", {'INPUT':currentBasePolygonLayer1,'DISTANCE':currentBuffDistance,'SEGMENTS':5,
    'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + '.gpkg'})
    
    processing.run("native:buffer", {'INPUT':currentBasePolygonLayer2,'DISTANCE':currentBuffDistance,'SEGMENTS':5,
    'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + '.gpkg'})
    
    
    
    processing.run("native:difference", {'INPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + '.gpkg',
    'OVERLAY':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + '.gpkg','OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Safe.gpkg','GRID_SIZE':None})
    
    processing.run("native:difference", {'INPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + '.gpkg',
    'OVERLAY':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + '.gpkg','OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Safe.gpkg','GRID_SIZE':None})
    
    
    currentSimpFactor = currentSimpFactor * 0.5
    
    processing.run("native:simplifygeometries", {'INPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Safe.gpkg','METHOD':0,
    'TOLERANCE':currentSimpFactor,'OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Simped.gpkg'})
    
    processing.run("native:simplifygeometries", {'INPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Safe.gpkg','METHOD':0,
    'TOLERANCE':currentSimpFactor,'OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Simped.gpkg'})
    
    
    
    processing.run("native:buffer", {'INPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Simped.gpkg','DISTANCE':-1 * currentSimpFactor,'SEGMENTS':5,
    'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Inward.gpkg'})
    
    processing.run("native:buffer", {'INPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Simped.gpkg','DISTANCE':-1 * currentSimpFactor,'SEGMENTS':5,
    'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Inward.gpkg'})
    
    
    
    processing.run("native:mergevectorlayers", {'LAYERS':[processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Inward.gpkg',currentBasePolygonLayer1],
    'CRS':None,'OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Merged.gpkg'})
    
    processing.run("native:mergevectorlayers", {'LAYERS':[processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Inward.gpkg',currentBasePolygonLayer2],
    'CRS':None,'OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Merged.gpkg'})
    
    
    
    processing.run("native:dissolve", {'INPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Merged.gpkg','FIELD':[],'SEPARATE_DISJOINT':False,
    'OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Dissolved.gpkg'})
    
    processing.run("native:dissolve", {'INPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Merged.gpkg','FIELD':[],'SEPARATE_DISJOINT':False,
    'OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Dissolved.gpkg'})
    
    
    
    currentBasePolygonLayer1 = processDirectory + 'PolygonLayer1Buffer' + str(currentBuffDistance) + 'Dissolved.gpkg'
    currentBasePolygonLayer2 = processDirectory + 'PolygonLayer2Buffer' + str(currentBuffDistance) + 'Dissolved.gpkg'
    
    
    currentBuffDistance = currentBuffDistance / 2


"""
##########################################################
Final tidying
"""


processing.run("native:simplifygeometries", {'INPUT':currentBasePolygonLayer1,'METHOD':2,'TOLERANCE':errorTolerance / 2,'OUTPUT':processDirectory + 'PolygonLayer1BuffedSimped.gpkg'})


processing.run("native:snapgeometries", {'INPUT':processDirectory + 'PolygonLayer1BuffedSimped.gpkg','REFERENCE_LAYER':polygonLayer1,'TOLERANCE':errorTolerance,'BEHAVIOR':0,
    'OUTPUT':processDirectory + 'PolygonLayer1BufferSimpedSnapped.gpkg'})
    
processing.run("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer1BufferSimpedSnapped.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixed.gpkg'})


processing.run("native:snapgeometries", {'INPUT':currentBasePolygonLayer2,'REFERENCE_LAYER':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixed.gpkg','TOLERANCE':errorTolerance,'BEHAVIOR':0,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferSnapped.gpkg'})

processing.run("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer2BufferSnapped.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferSnappedFixed.gpkg'})
    
    
    
processing.run("native:snapgeometries", {'INPUT':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixed.gpkg','REFERENCE_LAYER':processDirectory + 'PolygonLayer2BufferSnappedFixed.gpkg','TOLERANCE':errorTolerance,'BEHAVIOR':0,
    'OUTPUT':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixedSnapped.gpkg'})
    
processing.runAndLoadResults("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixedSnapped.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixedSnappedFixed.gpkg'})



processing.run("native:snapgeometries", {'INPUT':processDirectory + 'PolygonLayer2BufferSnappedFixed.gpkg','REFERENCE_LAYER':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixedSnappedFixed.gpkg','TOLERANCE':errorTolerance,'BEHAVIOR':0,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferSnappedFixedSnapped.gpkg'})

processing.runAndLoadResults("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer2BufferSnappedFixedSnapped.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferSnappedFixedSnappedFixed.gpkg'})

    
    
