


import os
import datetime
import arcpy
import utilities
from arcpy.sa import *

if os.path.exists("{0}.gdb".format(utilities.gdb_path)):
    print "Geodatabase already exists"
else:
    # Creates raster mosaics of Hansen loss and burn year out of the necessary tiles
    print "Creating geodatabase and loss and fire raster mosaics"
    utilities.create_mosaics()

# # Creates PRODES primary forest layers for 2007 to 2017 using the most recently released PRODES raster.
# # This only needs to be run once to create the annual PRODES primary forest rasters.
# utilities.create_annual_PRODES_recent()

# Iterates through years to get loss under various exclusion criteria in each year
for year in range(2007, 2018):

    print "Processing loss in", year

    # One or two digit year used for processing
    short_year = year - 2000

    # Names for output files under each criteria. Used for both tif and shp.
    loss_year = os.path.join(utilities.out_dir, "loss_{}".format(year))
    loss_year_noFire = os.path.join(utilities.out_dir, "loss_{}_noFire".format(year))
    loss_year_noFire_legal = os.path.join(utilities.out_dir, "loss_{}_noFire_legalAMZ".format(year))
    loss_year_noFire_legal_PRODES = os.path.join(utilities.out_dir, "loss_{}_noFire_legalAMZ_PRODES".format(year))
    loss_year_noFire_legal_PRODES_neighbor = os.path.join(utilities.out_dir, "loss_{}_noFire_legalAMZ_PRODES_neighbor".format(year))
    loss_year_noFire_legal_PRODES_neighbor_shp = os.path.join(utilities.out_dir, "loss_{}_noFire_legalAMZ_PRODES_neighbor_convert.shp".format(year))
    loss_year_noFire_legal_PRODES_neighbor_shp_dissolve = os.path.join(utilities.out_dir, "loss_{}_noFire_legalAMZ_PRODES_neighbor_convert_diss.shp".format(year))
    loss_year_noFire_legal_PRODES_neighbor_shp_dissolve_reproj = os.path.join(utilities.out_dir, "loss_{}_noFire_legalAMZ_PRODES_neighbor_convert_diss_reproj.shp".format(year))
    loss_year_noFire_legal_PRODES_neighbor_shp_dissolve_reproj_areas = os.path.join(utilities.out_dir, "loss_{}_noFire_legalAMZ_PRODES_neighbor_convert_diss_reproj_areas.shp".format(year))
    loss_year_noFire_legal_PRODES_neighbor_shp_dissolve_reproj_areas_large = os.path.join(utilities.out_dir, "loss_{}_noFire_legalAMZ_PRODES_neighbor_convert_diss_reproj_areas_large.shp".format(year))

    # Annual PRODES primary forest extents
    PRODES_prim = os.path.join(utilities.dir, utilities.PRODES_folder, "PRODES_primary_forest_{}.tif".format(year))

    # Masks loss to the given year
    print "  Masking loss to", year
    print "    Start time is", str(datetime.datetime.now())
    arcpy.gp.Con_sa("{0}.gdb/{1}".format(utilities.gdb_path, utilities.Hansen_mosaic), "{0}.gdb/{1}".format(utilities.gdb_path, utilities.Hansen_mosaic),
                    "{}.tif".format(loss_year), "",
                    '"Value" = {}'.format(short_year))
    print "    End time is", str(datetime.datetime.now())

    # Masks loss to pixels that were not burned (Brazil exclusion criteria 1).
    # Uses a merged burn year raster instead of a raster mosaic dataset because I couldn't get Con to work on the mosaic for some reason.
    # However, I did get it to work on a single raster of all the burn tiled merged after I create an attribute table for it,
    # so I used the merged raster instead.
    # For loss in 2001, only considers burn pixels from 2001 because considering previous year burning would include "0",
    # which means no burning was observed.
    if short_year == 1:

        print "  Removing loss pixels with fire in", year, "or", year-1
        print "    Start time is", str(datetime.datetime.now())
        arcpy.gp.Con_sa(os.path.join(utilities.dir, utilities.burnyear_merge), "{}.tif".format(loss_year),
                        "{}.tif".format(loss_year_noFire), "",
                        '"Value" NOT IN ({0})'.format(short_year))
        print "    End time is", str(datetime.datetime.now())

    # For loss in all later years (after 2001), considers burn pixels from the loss year and the preceding year.
    # Uses burn pixels from the loss year and previous year because loss could have occurred in the previous year but not been observed until the following year.
    else:

        print "  Removing loss pixels with fire in", year, "or", year-1
        print "    Start time is", str(datetime.datetime.now())
        arcpy.gp.Con_sa(os.path.join(utilities.dir, utilities.burnyear_merge), "{}.tif".format(loss_year),
                        "{}.tif".format(loss_year_noFire), "",
                        '"Value" NOT IN ({0}-1, {0})'.format(short_year))
        print "    End time is", str(datetime.datetime.now())

    # Clips loss to legal Amazon boundary (Brazil exclusion criteria 2)
    print "  Clipping loss raster to legal Amazon"
    print "    Start time is", str(datetime.datetime.now())
    arcpy.gp.ExtractByMask_sa("{}.tif".format(loss_year_noFire), utilities.legal_Amazon_reproj, "{}.tif".format(loss_year_noFire_legal))
    print "    End time is", str(datetime.datetime.now())

    # Clips loss to where there is PRODES primary forest from that year (Brazil exclusion criteria 3)
    print "  Clipping loss raster to loss in PRODES primary forest"
    print "    Start time is", str(datetime.datetime.now())
    arcpy.gp.ExtractByMask("{}.tif".format(loss_year_noFire_legal), PRODES_prim, "{}.tif".format(loss_year_noFire_legal_PRODES))
    print "    End time is", str(datetime.datetime.now())

    # Groups loss pixels into clusters of contiguous pixels (including diagonal pixels).
    # Each cluster gets its own ID number.
    print "  Grouping neighboring loss cells"
    print "    Start time is", str(datetime.datetime.now())
    outRegionGrp = RegionGroup("{}.tif".format(loss_year_noFire_legal_PRODES), "EIGHT", "WITHIN", "NO_LINK")
    print "Saving neighboring cells raster"
    outRegionGrp.save("{}.tif".format(loss_year_noFire_legal_PRODES_neighbor))
    print "    End time is", str(datetime.datetime.now())

    # Converts the grouped annual loss raster into a shapefile
    print "  Converting {0} loss raster to {0} loss polygon".format(year)
    print "    Start time is", str(datetime.datetime.now())
    arcpy.RasterToPolygon_conversion("{}.tif".format(loss_year_noFire_legal_PRODES_neighbor), loss_year_noFire_legal_PRODES_neighbor_shp, raster_field="Value", simplify="NO_SIMPLIFY")
    print "    Dissolving features into contiguous forest features"
    arcpy.Dissolve_management(loss_year_noFire_legal_PRODES_neighbor_shp, loss_year_noFire_legal_PRODES_neighbor_shp_dissolve, dissolve_field=["gridcode"], multi_part="MULTI_PART")
    print "    End time is", str(datetime.datetime.now())

    print "  Reprojecting {} loss area to World Eckert IV".format(year)
    print "    Start time is", str(datetime.datetime.now())
    out_coordinate_system = "PROJCS['World_Eckert_IV',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Eckert_IV'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],UNIT['Meter',1.0]]"
    arcpy.Project_management(loss_year_noFire_legal_PRODES_neighbor_shp_dissolve, loss_year_noFire_legal_PRODES_neighbor_shp_dissolve_reproj, out_coor_system=out_coordinate_system, transform_method="")
    print "    End time is", str(datetime.datetime.now())

    print "  Calculating feature areas"
    print "    Start time is", str(datetime.datetime.now())
    arcpy.CalculateAreas_stats(loss_year_noFire_legal_PRODES_neighbor_shp_dissolve_reproj, loss_year_noFire_legal_PRODES_neighbor_shp_dissolve_reproj_areas)
    print "    End time is", str(datetime.datetime.now())

    # Keeps only the features that are larger than 6.25 ha (Brazil exclusion criteria 4)
    print "  Selecting features larger than 6.25 ha"
    print "    Start time is", str(datetime.datetime.now())
    where = "F_AREA > 62500"
    arcpy.MakeFeatureLayer_management(loss_year_noFire_legal_PRODES_neighbor_shp_dissolve_reproj_areas, "layer_{}".format(year), where_clause=where)
    arcpy.CopyFeatures_management("layer_{}".format(year), loss_year_noFire_legal_PRODES_neighbor_shp_dissolve_reproj_areas_large)
    print "    End time is", str(datetime.datetime.now())


    # Converts all the rasters to shapefiles so that their areas and emissions calculated
    print "  Converting rasters to shapefiles"
    arcpy.RasterToPolygon_conversion("{}.tif".format(loss_year),
                                     "{}.shp".format(loss_year),
                                     "NO_SIMPLIFY", "VALUE")
    arcpy.RasterToPolygon_conversion("{}.tif".format(loss_year_noFire),
                                     "{}.shp".format(loss_year_noFire),
                                     "NO_SIMPLIFY", "VALUE")
    arcpy.RasterToPolygon_conversion("{}.tif".format(loss_year_noFire_legal),
                                     "{}.shp".format(loss_year_noFire_legal),
                                     "NO_SIMPLIFY", "VALUE")
    arcpy.RasterToPolygon_conversion("{}.tif".format(loss_year_noFire_legal_PRODES),
                                     "{}.shp".format(loss_year_noFire_legal_PRODES),
                                     "NO_SIMPLIFY", "VALUE")
    arcpy.RasterToPolygon_conversion("{}.tif".format(loss_year_noFire_legal_PRODES_neighbor),
                                     "{}.shp".format(loss_year_noFire_legal_PRODES_neighbor),
                                     "NO_SIMPLIFY", "VALUE")