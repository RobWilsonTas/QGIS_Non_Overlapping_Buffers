import time, glob
from pathlib import Path
startTime = time.time()


"""
##########################################################
User options 
"""

#Initial variable assignment
polygonLayer = 'D:/PolyLayer.gpkg' 

identifyingColumn = 'layer'

errorTolerance = 10

gridCellSize = errorTolerance * 400



"""
#######################################################################
#######################################################################
"""


#Making a folder for processing
rootProcessDirectory = str(Path(polygonLayer).parent.absolute()).replace('\\','/') + '/'
processDirectory = rootProcessDirectory + 'VoronoiProcess' + '/'
if not os.path.exists(processDirectory): os.mkdir(processDirectory)

tileDirectory = processDirectory + 'Tiles' + '/'
if not os.path.exists(tileDirectory): os.mkdir(tileDirectory)

outputsDirectory = processDirectory + 'Outputs' + '/'
if not os.path.exists(outputsDirectory): os.mkdir(outputsDirectory)


poly = QgsVectorLayer(polygonLayer)
polyExtent = poly.extent()

xmin = polyExtent.xMinimum()
xmax = polyExtent.xMaximum()
ymin = polyExtent.yMinimum()
ymax = polyExtent.yMaximum()
extentCoords = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)
extentCoordsNProj = extentCoords + ' [' + poly.crs().authid() + ']'

"""
##########################################################
Looped processing
"""


processing.run("native:creategrid", {'TYPE':2,'EXTENT':extentCoordsNProj,'HSPACING':gridCellSize,'VSPACING':gridCellSize,'HOVERLAY':0,'VOVERLAY':0,'CRS':QgsCoordinateReferenceSystem(poly.crs().authid()),
    'OUTPUT':processDirectory + 'GridOfTiles.gpkg'})
        
processing.run("native:extractbylocation", {'INPUT':processDirectory + 'GridOfTiles.gpkg','PREDICATE':[0],'INTERSECT':polygonLayer,'OUTPUT':processDirectory + 'GridOfTilesExtracted.gpkg'})


processing.run("native:splitvectorlayer", {'INPUT':processDirectory + 'GridOfTilesExtracted.gpkg','FIELD':'fid','PREFIX_FIELD':True,'FILE_TYPE':0,'OUTPUT':tileDirectory})



tileFiles = glob.glob(tileDirectory + '*.gpkg')

x = 0
for currentTile in tileFiles:

    x = x + 1
    
    if x > 0: #This can be adjusted to be a different value if you get part the way through and need to resume at a later date
        
        subProcessDirectory = processDirectory + 'Tile' + str(x) + '/'
        if not os.path.exists(subProcessDirectory): os.mkdir(subProcessDirectory)
        
        
        
        processing.run("native:buffer", {'INPUT':currentTile,'DISTANCE':errorTolerance,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,
            'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':subProcessDirectory + 'BufferedTile' + str(x) + '.gpkg'})
        
        
        processing.run("native:clip", {'INPUT':polygonLayer,'OVERLAY':subProcessDirectory + 'BufferedTile' + str(x) + '.gpkg','OUTPUT':subProcessDirectory + 'ClippedPoly' + str(x) + '.gpkg'})
        


        processing.run("native:buffer", {'INPUT':subProcessDirectory + 'ClippedPoly' + str(x) + '.gpkg','DISTANCE':-0.5 * errorTolerance,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,
            'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':subProcessDirectory + 'ClippedPoly' + str(x) + 'Inward.gpkg'})
            
            
        processing.run("native:simplifygeometries", {'INPUT':subProcessDirectory + 'ClippedPoly' + str(x) + 'Inward.gpkg','METHOD':0,'TOLERANCE':errorTolerance * 0.5,'OUTPUT':subProcessDirectory + 'ClippedPoly' + str(x) + 'InwardSimp.gpkg'})


        tile = QgsVectorLayer(currentTile)
        tileExtent = tile.extent()

        tilexmin = tileExtent.xMinimum()
        tilexmax = tileExtent.xMaximum()
        tileymin = tileExtent.yMinimum()
        tileymax = tileExtent.yMaximum()
        tileExtentCoords = "%f,%f,%f,%f" %(tilexmin, tilexmax, tileymin, tileymax)
        tileExtentCoordsNProj = tileExtentCoords + ' [' + tile.crs().authid() + ']'

        processing.run("native:creategrid", {'TYPE':2,'EXTENT':tileExtentCoordsNProj,'HSPACING':errorTolerance * 0.5,'VSPACING':errorTolerance * 0.5,'HOVERLAY':0,'VOVERLAY':0,'CRS':QgsCoordinateReferenceSystem(poly.crs().authid()),
            'OUTPUT':subProcessDirectory + 'Grid' + str(x) + '.gpkg'})
        


        processing.run("native:joinbynearest", {'INPUT':subProcessDirectory + 'Grid' + str(x) + '.gpkg','INPUT_2':subProcessDirectory + 'ClippedPoly' + str(x) + 'Inward.gpkg',
            'FIELDS_TO_COPY':[],'DISCARD_NONMATCHING':False,'PREFIX':'','NEIGHBORS':1,'MAX_DISTANCE':None,'OUTPUT':subProcessDirectory + 'Grid' + str(x) + 'Joined.gpkg'})


        processing.run("native:dissolve", {'INPUT':subProcessDirectory + 'Grid' + str(x) + 'Joined.gpkg','FIELD':['layer'],'SEPARATE_DISJOINT':False,'OUTPUT':outputsDirectory + 'Grid' + str(x) + 'JoinedDissolved.gpkg'})



outputFiles = glob.glob(outputsDirectory + '*.gpkg')

processing.run("native:mergevectorlayers", {'LAYERS':outputFiles,'CRS':None,'OUTPUT':processDirectory + 'VoronoisTogether.gpkg'})

processing.run("native:dissolve", {'INPUT':processDirectory + 'VoronoisTogether.gpkg','FIELD':[identifyingColumn],'SEPARATE_DISJOINT':False,
        'OUTPUT':processDirectory + 'VoronoisTogetherDissolved.gpkg'})
        
processing.runAndLoadResults("native:extractbyextent", {'INPUT':processDirectory + 'VoronoisTogetherDissolved.gpkg','EXTENT':extentCoordsNProj,'CLIP':True,'OUTPUT':processDirectory + 'VoronoisTogetherDissolvedClipped.gpkg'})
    
    
endTime = time.time()
totalTime = endTime - startTime
print("With a grid size of " + str(gridCellSize) + " this took " + str(int(totalTime)) + " seconds")
    
