import glob
import os
import arcpy
import subprocess
import pandas as pd
import utilities

os.chdir(utilities.out_dir)

all_shp = glob.glob('*.shp')
print all_shp

for shp in all_shp:

    shp_name = shp[:-4]
    print "Processing", shp

    # Adds the file name to a new column in the shapefile
    arcpy.AddField_management(os.path.join(utilities.out_dir, shp), field_name="name", field_type="TEXT", field_precision="",
                              field_scale="", field_length="100", field_alias="", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")
    arcpy.CalculateField_management(os.path.join(utilities.out_dir, shp), field="name", expression='"{}"'.format(shp_name),
                                    expression_type="PYTHON", code_block="")





