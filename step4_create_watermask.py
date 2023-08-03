# -*- coding: utf-8 -*-
# use ArcPy in ArcGIS 10.6.1
#author = "Wensong Zhang"
#copyright = "Copyright 2023, Nanjing Greenland Hydrology Group"
#license = "GPL"
#version = "0.1"
#maintainer = "Wensong Zhang"
#email = "wensong_z@outlook.com"
#status = "Production"
#description = "apply thresholds to NDWI and PPO images, then combine the two results together"

import arcpy, os, sys
from arcpy import env
from arcpy.sa import *
import pandas as pd

# parameter 1, the list contains all images and thresholds (Table S1 in our manuscript)
image_list = r"E:\Pan_GrIS_Sentinel_2\table_S1_of_the_manuscript.xls"
# parameter 2, the output path of step2, now becomes the input path of this code
ndwiFilePath = r'E:\Pan_GrIS_Sentinel_2\step2_masked_NDWI'
# parameter 3, the output path of step3, now also becomes the input path of this code
ppoFilePath = r'E:\Pan_GrIS_Sentinel_2\step3_Gabor_PPO'
# parameter 4, the output path of this code
outputPath = r'E:\Pan_GrIS_Sentinel_2\step4_watermask'

# this path will be automatically created, if it doesn't exist 
temp_path = r'E:\Pan_GrIS_Sentinel_2\step4_watermask\temp'

env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
env.workspace = outputPath
env.extent = "MAXOF"  # this sentence is important to keeep the same extent during processing

try:
    os.makedirs(outputPath)
except OSError:
    if not os.path.isdir(outputPath):
        raise
try:
    os.makedirs(temp_path)
except OSError:
    if not os.path.isdir(temp_path):
        raise

df_image_list = pd.DataFrame(pd.read_excel(image_list))
df_image_list.index = df_image_list['ID'].astype('int')

print df_image_list

for index, row in df_image_list.iterrows():
    if row['PROCESS'] !=0:
        continue

    tndwi = row['T1']
    tgabor = row['T2']  # the thredhold to classify raster and get river mask, default 20

    ndwiFile = "mask_ice_ndwi_stack_" + row['NAME']
    gaborFile = ndwiFile.split('.tif')[0] + "_bandpass_gabor_cpo20.tif"
    ndwiFile_path = os.path.join(ndwiFilePath, ndwiFile)
    gaborFile_path = os.path.join(ppoFilePath, gaborFile)

    print tndwi, tgabor, ndwiFile

    watermaskFile = os.path.join(outputPath, "temp_watermask_" + ndwiFile_path.split('.tif')[0] + "_tg_" + str(tgabor) + "_tn_" + str(tndwi) + ".tif")

    #creat river and lake mask
    riverRaster = Con(Raster(gaborFile_path) >= tgabor, 1, 0)
    lakeRaster = Con(Raster(ndwiFile_path) >= tndwi, 1, 0)
    rivermaskFile = os.path.join(temp_path, "river_" + ndwiFile.split('.tif')[0] + "_tg_" + str(tgabor) + ".tif")
    riverRaster.save(rivermaskFile)
    lakemaskFile = os.path.join(temp_path, "lake_" + ndwiFile.split('.tif')[0] + "_tn_" + str(tndwi) + ".tif")
    lakeRaster.save(lakemaskFile)

    #creat meltwater mask
    temp_waterRaster = Raster(rivermaskFile) + Raster(lakemaskFile)
    temp_watermaskFile = os.path.join(temp_path, "temp_river_lake_" + ndwiFile.split('.tif')[0] + "_tg_" + str(tgabor) + "_tn_" + str(tndwi) + ".tif")
    temp_waterRaster.save(temp_watermaskFile)
    finalwaterRaster = Reclassify(temp_waterRaster, "Value", "0 0; 1 1; 2 1", "NODATA")
    finalwatermaskFile = os.path.join(outputPath, "temp_watermask_" + temp_watermaskFile.split('temp_river_lake_')[1])
    finalwaterRaster.save(finalwatermaskFile)

    #update image process record
    df_image_list.at[index, 'PROCESS'] = 1


    arcpy.Delete_management(temp_watermaskFile)
    arcpy.CalculateStatistics_management(finalwatermaskFile)
    arcpy.BuildPyramids_management(finalwatermaskFile)
    arcpy.Delete_management("in_memory")
    print finalwatermaskFile

#save image list
df_image_list.to_excel(image_list,columns=['ID','NAME','T1','T2','PROCESS'])
