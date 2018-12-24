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

    ###### Not actually using, but a useful code snippet for converting shapefiles into tsvs
    # # Converts the shapefile to a csv
    # cmd = ['ogr2ogr', '-f', 'CSV', '{}.csv'.format(shp_name), '{}.shp'.format(shp_name), '-lco', 'GEOMETRY=AS_WKT', '-overwrite', '-progress']
    # subprocess.check_call(cmd)
    #
    # # Formats the csv correctly for input to Hadoop and outputs the expected tsv
    # file = pd.read_csv('{}.csv'.format(shp_name))
    # file_formatted = file.drop(['Id', 'gridcode'], axis=1)
    # file_formatted['bound1'], file_formatted['bound2'], file_formatted['bound3'], file_formatted['bound4'], file_formatted['iso'], file_formatted['adm1'], file_formatted['adm2'], file_formatted['extra'] = [1, 1, 1, 1, 'ZZZ', '1', '1', '1']
    # file_formatted_head = file_formatted.head(100)
    # print list(file_formatted_head.columns.values)
    # file_formatted_head.to_csv('{}.tsv'.format(shp_name), sep='\t', index=False, header=False)

    # sys.exit()



