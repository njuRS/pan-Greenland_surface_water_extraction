# -*- coding: utf-8 -*-
# use ArcPy in ArcGIS 10.6.1
#author = "Wensong Zhang"
#copyright = "Copyright 2023, Nanjing Greenland Hydrology Group"
#license = "GPL"
#version = "0.1"
#maintainer = "Wensong Zhang"
#email = "wensong_z@outlook.com"
#status = "Production"
#description = "extract Sentinel-2 image by Greenland Mapping Project (GIMP) Ice Mask"

import arcpy,os,sys
import os
import shutil
from arcpy import env
from arcpy.sa import *

# parameter 1, the output path of step1, now becomes the input path of this code
inputPath = r"E:\Pan_GrIS_Sentinel_2\step1_NDWI"
# parameter 2, the output path of this code
outputPath = r"E:\Pan_GrIS_Sentinel_2\step2_masked_NDWI"

env.workspace= inputPath

# parameter 3, the Greenland Mapping Project (GIMP) Ice Mask
mask_shp = r"E:\Pan_GrIS_Sentinel_2_GIMP1_2\base_data\GIMP_GrIS_90m_2015_v1_2.shp"

#if outputPath did not exsist, create the folder
try: 
    os.makedirs(outputPath)
except OSError:
    if not os.path.isdir(outputPath):
        raise


rasters=arcpy.ListRasters("*", "tif")
for raster in rasters:
    print(raster)  

    extract_RS_Raster  ="mask_ice_" + raster
    extract_RS_Raster1 = ExtractByMask(raster, mask_shp)
    extract_RS_Raster1.save(os.path.join(outputPath,extract_RS_Raster))
    arcpy.CalculateStatistics_management(extract_RS_Raster1)
    arcpy.BuildPyramids_management(extract_RS_Raster1)
    arcpy.Delete_management("in_memory")
    print(extract_RS_Raster1)