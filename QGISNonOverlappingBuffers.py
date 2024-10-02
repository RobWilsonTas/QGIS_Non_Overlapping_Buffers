import datetime
from pathlib import Path
startTime = datetime.time()


"""
##########################################################
User options for the tiling section
"""

#Initial variable assignment
polygonLayer1 = 'D:/PublicLand.gpkg' 
polygonLayer2 = 'D:/PrivateLand.gpkg' 

maximumGap = 50
errorTolerance = 10


"""
#######################################################################
#######################################################################
"""


#Making a folder for processing
rootProcessDirectory = str(Path(polygonLayer1).parent.absolute()).replace('\\','/') + '/'
processDirectory = rootProcessDirectory + 'ProcessBuffer' + '/'
if not os.path.exists(processDirectory): os.mkdir(processDirectory)


"""
##########################################################
Looped processing
"""


currentBasePolygonLayer1 = polygonLayer1
currentBasePolygonLayer2 = polygonLayer2


for currentBufferNumber in range(int(maximumGap / (errorTolerance / 4.1))):
    
    processing.run("native:buffer", {'INPUT':currentBasePolygonLayer1,'DISTANCE':errorTolerance / 4.1,'SEGMENTS':5,
    'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + '.gpkg'})
    
    processing.run("native:buffer", {'INPUT':currentBasePolygonLayer2,'DISTANCE':errorTolerance / 4.1,'SEGMENTS':5,
    'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + '.gpkg'})
    
    
    
    processing.run("native:difference", {'INPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + '.gpkg',
    'OVERLAY':processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + '.gpkg','OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + 'Safe.gpkg','GRID_SIZE':None})
    
    processing.run("native:difference", {'INPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + '.gpkg',
    'OVERLAY':processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + '.gpkg','OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + 'Safe.gpkg','GRID_SIZE':None})
    
    
    processing.run("native:mergevectorlayers", {'LAYERS':[processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + 'Safe.gpkg',currentBasePolygonLayer1],
    'CRS':None,'OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + 'Merged.gpkg'})
    
    processing.run("native:mergevectorlayers", {'LAYERS':[processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + 'Safe.gpkg',currentBasePolygonLayer2],
    'CRS':None,'OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + 'Merged.gpkg'})
    
    
    
    processing.run("native:dissolve", {'INPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + 'Merged.gpkg','FIELD':[],'SEPARATE_DISJOINT':False,
    'OUTPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + 'Dissolved.gpkg'})
    
    processing.run("native:dissolve", {'INPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + 'Merged.gpkg','FIELD':[],'SEPARATE_DISJOINT':False,
    'OUTPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + 'Dissolved.gpkg'})
    
    
    
    currentBasePolygonLayer1 = processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + 'Dissolved.gpkg'
    currentBasePolygonLayer2 = processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + 'Dissolved.gpkg'
    


"""
##########################################################
Tidy up and snap
"""


processing.run("native:simplifygeometries", {'INPUT':currentBasePolygonLayer1,'METHOD':2,'TOLERANCE':errorTolerance,'OUTPUT':processDirectory + 'PolygonLayer1BuffedSimped.gpkg'})

processing.run("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer1BuffedSimped.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer1BuffedSimpedFixed.gpkg'})
    

processing.run("native:snapgeometries", {'INPUT':processDirectory + 'PolygonLayer1BuffedSimpedFixed.gpkg','REFERENCE_LAYER':polygonLayer1,'TOLERANCE':errorTolerance,'BEHAVIOR':0,
    'OUTPUT':processDirectory + 'PolygonLayer1BufferSimpedSnapped.gpkg'})
    
processing.run("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer1BufferSimpedSnapped.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixed.gpkg'})



processing.run("native:snapgeometries", {'INPUT':currentBasePolygonLayer2,'REFERENCE_LAYER':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixed.gpkg','TOLERANCE':errorTolerance,'BEHAVIOR':0,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferSnapped.gpkg'})

processing.run("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer2BufferSnapped.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferSnappedFixed.gpkg'})
    
    
    
"""
##########################################################
Provide a final buffering after snapping
"""
    
    

processing.run("native:buffer", {'INPUT':processDirectory + 'PolygonLayer1BufferSimpedSnappedFixed.gpkg','DISTANCE':errorTolerance / 4.1,'SEGMENTS':5,
'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRun.gpkg'})
    
processing.run("native:buffer", {'INPUT':processDirectory + 'PolygonLayer2BufferSnappedFixed.gpkg','DISTANCE':errorTolerance / 4.1,'SEGMENTS':5,
'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRun.gpkg'})
    
    

processing.run("native:difference", {'INPUT':processDirectory + 'PolygonLayer1Buffer' + str(currentBufferNumber) + '.gpkg',
'OVERLAY':processDirectory + 'PolygonLayer2BufferFinalRun.gpkg','OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRunSafe.gpkg','GRID_SIZE':None})

processing.run("native:difference", {'INPUT':processDirectory + 'PolygonLayer2Buffer' + str(currentBufferNumber) + '.gpkg',
'OVERLAY':processDirectory + 'PolygonLayer1BufferFinalRun.gpkg','OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunSafe.gpkg','GRID_SIZE':None})


processing.run("native:mergevectorlayers", {'LAYERS':[processDirectory + 'PolygonLayer1BufferFinalRunSafe.gpkg',currentBasePolygonLayer1],
'CRS':None,'OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRunMerged.gpkg'})

processing.run("native:mergevectorlayers", {'LAYERS':[processDirectory + 'PolygonLayer2BufferFinalRunSafe.gpkg',currentBasePolygonLayer2],
'CRS':None,'OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunMerged.gpkg'})



processing.run("native:dissolve", {'INPUT':processDirectory + 'PolygonLayer1BufferFinalRunMerged.gpkg','FIELD':[],'SEPARATE_DISJOINT':False,
'OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolved.gpkg'})

processing.run("native:dissolve", {'INPUT':processDirectory + 'PolygonLayer2BufferFinalRunMerged.gpkg','FIELD':[],'SEPARATE_DISJOINT':False,
'OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolved.gpkg'})


    
"""
##########################################################
Final snapping
"""

processing.run("native:multiparttosingleparts", {'INPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolved.gpkg','OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingle.gpkg'})

processing.run("native:multiparttosingleparts", {'INPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolved.gpkg','OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingle.gpkg'})



processing.run("native:extractbyexpression", {'INPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingle.gpkg','EXPRESSION':'$area > ' + str(errorTolerance ** 2),
'OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingleFilter.gpkg'})

processing.run("native:extractbyexpression", {'INPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingle.gpkg','EXPRESSION':'$area > ' + str(errorTolerance ** 2),
'OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFilter.gpkg'})



processing.run("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingleFilter.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingleFixed.gpkg'})

processing.run("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFilter.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFixed.gpkg'})



processing.run("native:simplifygeometries", {'INPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingleFixed.gpkg','METHOD':0,'TOLERANCE':errorTolerance/3,
    'OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingleFixedSimp.gpkg'})
    
processing.run("native:simplifygeometries", {'INPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFixed.gpkg','METHOD':0,'TOLERANCE':errorTolerance/3,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFixedSimp.gpkg'})
   
    
processing.run("native:snapgeometries", {'INPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFixedSimp.gpkg','REFERENCE_LAYER':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingleFixedSimp.gpkg',
    'TOLERANCE':errorTolerance,'BEHAVIOR':1,'OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFixedSimpSnapped.gpkg'})

processing.run("native:fixgeometries", {'INPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFixedSimpSnapped.gpkg','METHOD':1,
    'OUTPUT':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFixedSimpSnappedFixed.gpkg'})
    
#############
  
    
    
processing.run("native:snapgeometries", {'INPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingleFixedSimp.gpkg','REFERENCE_LAYER':processDirectory + 'PolygonLayer2BufferFinalRunDissolvedSingleFixedSimpSnappedFixed.gpkg',
    'TOLERANCE':errorTolerance,'BEHAVIOR':2,'OUTPUT':processDirectory + 'PolygonLayer1BufferFinalRunDissolvedSingleFixedSimpSnapped.gpkg'})
    

    

    
    
