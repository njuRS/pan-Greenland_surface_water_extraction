# -*- coding: utf-8 -*-
# use ArcPy in ArcGIS 10.6.1
#author = "Wensong Zhang"
#copyright = "Copyright 2023, Nanjing Greenland Hydrology Group"
#license = "GPL"
#version = "0.1"
#maintainer = "Wensong Zhang"
#email = "wensong_z@outlook.com"
#status = "Production"
#description = "calculate NDWI of all visible Sentinel-2 images in a MXD document"

import arcpy,os,sys
import os
import shutil
from arcpy import env
import arcpy.mapping as mapping
from arcpy.sa import *
import pandas as pd
import traceback

def main():
    arcpy.CheckOutExtension("Spatial")
    env.extent="MAXOF"
    arcpy.env.overwriteOutput = True
    arcpy.env.parallelProcessingFactor = 8

    # parameter 1, the mxd document which contains all visible Sentinel-2 images 
    #     note that in our Sentinel-2 images, green band is band 2, and red band is band 4
    #     you can change the band number (in lines 61-67) according to your image
    mxd = arcpy.mapping.MapDocument(r"E:\Pan_GrIS_Sentinel_2\imagery.mxd")
    
    df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
    lyrs = arcpy.mapping.ListLayers(mxd,"*.tif",df)

    # parameter 2, the output path of this code
    output_path = "E:\\Pan_GrIS_Sentinel_2\\step1_NDWI\\"

    if os.path.exists(output_path)==False:
        os.mkdir(output_path)
        arcpy.env.workspace = output_path

    df_image_list = pd.DataFrame(columns=["ID","NAME","T1","T2","PROCESS"])

    i = 0
    for lyr in lyrs:
        if lyr.visible == True:
            print(lyr)
            i = i + 1

            lyr_path = lyr.dataSource
            lyr_name = os.path.basename(lyr_path)
            
            #caculate ndwi
            raster = lyr_path
            print(raster)
            filename = "ndwi_" + os.path.basename(raster)    #read filename in filepath  using os.path.basename(XXX)

            bandNamePrefix = "0"
            # in our Sentinel-2 images, green band is band 2, and red band is band 4
            # you can change the following band numbers to your numbers
            if arcpy.Exists(raster + "\\Band_2") and arcpy.Exists(raster + "\\Band_4"):
                    bandNamePrefix = "\\Band_"
            elif arcpy.Exists(raster + "\\B2") and arcpy.Exists(raster + "\\B4"):
                    bandNamePrefix = "\\B"

            greenband = Raster(raster + bandNamePrefix + "2")            #sentinel_2 after combands, green:band2 NIR:band7
            nirband   = Raster(raster + bandNamePrefix + "4")

            ndwiRaster = Float(greenband - nirband) / Float(greenband + nirband)
            print(output_path+filename)
            ndwiRaster.save(output_path+filename)
            arcpy.Delete_management("in_memory")
            
            df_image_list = df_image_list.append(pd.DataFrame({'ID':[int(i)],'NAME':[os.path.split(raster)[1]],'T1':[0.4],'T2':[15],'PROCESS':[0]}),ignore_index=True)

    print(df_image_list)

    df_image_list.to_excel(output_path+'\\table_S1.xls',columns=['ID','NAME','T1','T2','PROCESS'])

if __name__ == "__main__":
    main()
