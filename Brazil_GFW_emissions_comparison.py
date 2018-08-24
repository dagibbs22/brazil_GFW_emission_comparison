import os
import datetime
import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")

dir = "C:\\GIS\\GFW_Climate\\Brazil_emis_comparison"

gdb = "loss_mosaics"
Hansen_mosaic = "Hansen_loss_2017"
burn_mosaic = "burn_loss_from_s3"
gdb_path = os.path.join(dir, gdb)
Hansen_loss_tile_path = os.path.join(dir, Hansen_mosaic)
fire_loss_tile_path = os.path.join(dir, burn_mosaic)
loss_tile = "C:\\GIS\\GFW_Climate\\Brazil_emis_comparison\\Hansen_loss_2017\\00N_050W.tif"

legal_Amazon_reproj = "C:\\GIS\\Multi_project\\Brazil_legal_Amazon\\prodes_full_extent_reproj.shp"

prim_2007_17 = os.path.join(dir, "PDigital2017_AMZ_30m.tif")
prim_2007_17_reclass = os.path.join(dir, "PDigital2017_AMZ_30m_reclass.tif")

loss_noFire = os.path.join(dir, "loss_noFire.tif")
loss_noFire_legal = os.path.join(dir, "loss_noFire_legalAMZ.tif")

non_burn_area = os.path.join(dir, "non_burn_area_01_17.tif")

# print "Creating geodatabase for loss and fire mosaics in Amazonia..."
# out_coor_system = arcpy.Describe(loss_tile).spatialReference
# print "  Creating gdb..."
# arcpy.CreateFileGDB_management(dir, gdb)
#
# print "  Creating Hansen loss mosaic..."
# arcpy.CreateMosaicDataset_management("{}.gdb".format(gdb_path), Hansen_mosaic, out_coor_system, num_bands="1",
#                                      pixel_type="8_BIT_UNSIGNED")
# print "  Adding Hansen loss tiles to mosaic..."
# arcpy.AddRastersToMosaicDataset_management("{0}.gdb/{1}".format(gdb_path, Hansen_mosaic),
#                                            raster_type="Raster Dataset", input_path=Hansen_loss_tile_path)
#
# print "  Creating fire loss mosaic..."
# arcpy.CreateMosaicDataset_management("{}.gdb".format(gdb_path), burn_mosaic, out_coor_system, num_bands="1",
#                                      pixel_type="8_BIT_UNSIGNED")
# print "  Adding fire loss tiles to mosaic..."
# arcpy.AddRastersToMosaicDataset_management("{0}.gdb/{1}".format(gdb_path, burn_mosaic),
#                                            raster_type="Raster Dataset", input_path=fire_loss_tile_path)
#
# print "Clipping loss raster to loss outside of fires"
# print "Start time is", str(datetime.datetime.now())
# print "  Creating raster of non-fire areas"
# outCon1 = arcpy.gp.Con_sa("{0}.gdb/{1}".format(gdb_path, burn_mosaic), "999", non_burn_area, "", "VALUE = 0")
# print "  Saving raster of non-fire areas"
# outCon1.save(non_burn_area)
# print "  Creating raster of loss in non-fire areas"
# arcpy.gp.ExtractByMask_sa("{0}.gdb/{1}".format(gdb_path, Hansen_mosaic), non_burn_area, loss_noFire)
# print "End time is", str(datetime.datetime.now())

# print "Clipping non-fire loss raster to legal Amazon"
# print "Start time is", str(datetime.datetime.now())
# arcpy.gp.ExtractByMask_sa(loss_noFire, legal_Amazon_reproj, loss_noFire_legal)
# print "End time is", str(datetime.datetime.now())
#
# This definition of PRODES primary forest is for the end of 2006. Primary forest is anything lost in 2007 or later or still primary forest
# print "Reclassifying PRODES primary forest raster"
# outReclass = Reclassify(prim_2007_17, "Value", RemapRange([[1,1,1], [2,5,"NODATA"], [6,24,1]]))
# print "Saving reclassified primary forest raster"
# outReclass.save(prim_2007_17_reclass)

for year in range(2015, 2018):

    loss_noFire_legal_year = os.path.join(dir, "loss_noFire_legalAMZ_{}.tif".format(year))
    loss_noFire_legal_year_PRODES = os.path.join(dir, "loss_noFire_legalAMZ_{}_PRODES.tif".format(year))
    loss_noFire_legal_year_PRODES_neighbor = os.path.join(dir, "loss_noFire_legalAMZ_{}_PRODES_neighbor.tif".format(year))
    loss_noFire_legal_year_PRODES_neighbor_shp = os.path.join(dir, "loss_noFire_legalAMZ_{}_PRODES_neighbor_convert.shp".format(year))
    loss_noFire_legal_year_PRODES_neighbor_shp_dissolve = os.path.join(dir, "loss_noFire_legalAMZ_{}_PRODES_neighbor_convert_diss.shp".format(year))
    loss_noFire_legal_year_PRODES_neighbor_shp_dissolve_reproj = os.path.join(dir, "loss_noFire_legalAMZ_{}_PRODES_neighbor_convert_diss_reproj.shp".format(year))
    loss_noFire_legal_year_PRODES_neighbor_shp_dissolve_reproj_areas = os.path.join(dir, "loss_noFire_legalAMZ_{}_PRODES_neighbor_convert_diss_reproj_areas.shp".format(year))
    loss_noFire_legal_year_PRODES_neighbor_shp_dissolve_reproj_areas_large = os.path.join(dir, "loss_noFire_legalAMZ_{}_PRODES_neighbor_convert_diss_reproj_areas_large.shp".format(year))

    short_year = year - 2000

    print "Masking loss raster to loss in year {}".format(year)
    print "Start time is", str(datetime.datetime.now())
    arcpy.gp.Con_sa(loss_noFire_legal, "1", loss_noFire_legal_year, "", '"Value"={}'.format(short_year))
    print "End time is", str(datetime.datetime.now())

    print "Clipping loss raster to loss in PRODES primary forest"
    print "Start time is", str(datetime.datetime.now())
    outExtractByMask3 = ExtractByMask(loss_noFire_legal_year, prim_2007_17_reclass)
    print "Saving loss raster clipped to PRODES primary forest"
    outExtractByMask3.save(loss_noFire_legal_year_PRODES)
    print "End time is", str(datetime.datetime.now())

    print "Grouping neighboring {} loss cells".format(year)
    print "Start time is", str(datetime.datetime.now())
    outRegionGrp = RegionGroup(loss_noFire_legal_year_PRODES, "EIGHT", "WITHIN", "NO_LINK")
    print "Saving neighboring cells raster"
    outRegionGrp.save(loss_noFire_legal_year_PRODES_neighbor)
    print "End time is", str(datetime.datetime.now())

    print "Converting {0} loss raster to {0} loss polygon".format(year)
    print "Start time is", str(datetime.datetime.now())
    arcpy.RasterToPolygon_conversion(loss_noFire_legal_year_PRODES_neighbor, loss_noFire_legal_year_PRODES_neighbor_shp, raster_field="Value", simplify="NO_SIMPLIFY")
    print "Dissolving features into contiguous forest features"
    arcpy.Dissolve_management(loss_noFire_legal_year_PRODES_neighbor_shp, loss_noFire_legal_year_PRODES_neighbor_shp_dissolve, dissolve_field=["gridcode"], multi_part="MULTI_PART")
    print "End time is", str(datetime.datetime.now())

    print "Reprojecting {} loss area to World Eckert IV".format(year)
    print "Start time is", str(datetime.datetime.now())
    out_coordinate_system = "PROJCS['World_Eckert_IV',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Eckert_IV'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],UNIT['Meter',1.0]]"
    arcpy.Project_management(loss_noFire_legal_year_PRODES_neighbor_shp_dissolve, loss_noFire_legal_year_PRODES_neighbor_shp_dissolve_reproj, out_coor_system=out_coordinate_system, transform_method="")
    print "End time is", str(datetime.datetime.now())

    print "Calculating feature areas"
    print "Start time is", str(datetime.datetime.now())
    arcpy.CalculateAreas_stats(loss_noFire_legal_year_PRODES_neighbor_shp_dissolve_reproj, loss_noFire_legal_year_PRODES_neighbor_shp_dissolve_reproj_areas)
    print "End time is", str(datetime.datetime.now())

    print "Selecting features larger than 6.25 ha"
    print "Start time is", str(datetime.datetime.now())
    where = "F_AREA > 62500"
    arcpy.MakeFeatureLayer_management(loss_noFire_legal_year_PRODES_neighbor_shp_dissolve_reproj_areas, "layer_{}".format(year), where_clause=where)
    arcpy.CopyFeatures_management("layer_{}".format(year), loss_noFire_legal_year_PRODES_neighbor_shp_dissolve_reproj_areas_large)
    print "End time is", str(datetime.datetime.now())
