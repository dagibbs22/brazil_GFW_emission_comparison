### This script applies four exclusions to Hansen tree cover loss that are used by Brazil's PRODES monitoring system
### in order to obtain the area of tree cover loss each year between 2001 and 2017 that meets Brazil's criteria for its
### official statistics.
### The four criteria are: loss must be within legal Amazon boundary, loss must not be in burned area,
### loss must be in PRODES primary forest, and loss must be >6.25 hectares.
### Inputs are:
### 1. Hansen loss clipped to legal Amazon boundary (boundary is from Liz Goldman)
### 2. Burned year (the year that the pixel was burned using MODIS data)
### 3. PRODES primary forest extent each year (keys are at http://www.dpi.inpe.br/prodesdigital/dadosn/mosaicos/class_rgb.txt)
### Two PRODES primary forest rasters used here: one that covers 2007 to 2017 and one that covers 2001 to 2014.
### The code below includes lines to make the PRODES annual primary forest from the 2007-2017 raster but not from
### the 2001-2014 raster; that must be made by manual geoprocessing.
### This results in two time series of tree cover loss: 2001-2014 and 2007-2017.
### For each year, the tool produces a series of tifs and shapefiles. The shapefiles can then have zonal statistics
### applied to them (e.g., Hadoop) to get emissions and tree cover loss for each year.


import os
import datetime
import arcpy
from osgeo import gdal
import utilities
from arcpy.sa import *

if os.path.exists(utilities.legal_Amazon_loss_dir):
    print "Loss clipped to Brazil boundary already exists"
else:
    # Creates raster mosaics of Hansen loss and burn year out of the necessary tiles
    print "Creating geodatabase and loss and fire raster mosaics"
    utilities.create_mosaics()

# # Creates PRODES primary forest layers for 2007 to 2017 using the most recently released PRODES raster.
# # This only needs to be run once to create the annual PRODES primary forest rasters.
# utilities.create_annual_PRODES_recent()

# Ranges for creating annual emissions maps using the early and recent PRODES primary forest rasters.
# The variable names in the for loop below must match the early/recent PRODES selection.
early_PRODES = [2001, 2015]
late_PRODES = [2007, 2018]

# Iterates through years to get loss under various exclusion criteria in each year
# for year in range(early_PRODES[0], early_PRODES[1]):
for year in range(early_PRODES[0], early_PRODES[1]):

    print "Processing loss in", year

    # One or two digit year used for processing
    short_year = year - 2000

    # For the early (2014) PRODES raster (2001-2014 primary forests)
    # Names for output files under each criteria. Used for both tif and shp.
    legal_loss_year = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early".format(year))
    legal_loss_year_PRODES = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early_PRODES".format(year))
    legal_loss_year_PRODES_noFire = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early_PRODES_noFire".format(year))
    legal_loss_year_PRODES_noFire_neighbor = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early_PRODES_noFire_neighbor".format(year))
    legal_loss_year_PRODES_noFire_neighbor_shp = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early_PRODES_noFire_neighbor_convert.shp".format(year))
    legal_loss_year_PRODES_noFire_neighbor_shp_dissolve = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early_PRODES_noFire_neighbor_convert_diss.shp".format(year))
    legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early_PRODES_noFire_neighbor_convert_diss_reproj.shp".format(year))
    legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj_areas = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early_PRODES_noFire_neighbor_convert_diss_reproj_areas.shp".format(year))
    legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj_areas_large = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_early_PRODES_noFire_neighbor_convert_diss_reproj_areas_large.shp".format(year))

    # Annual PRODES primary forest extents for the 2014 PRODES raster
    PRODES_prim = os.path.join(utilities.dir, utilities.PRODES_folder, "PRODES_primary_forest_{}_early_raster.tif".format(year))

    # # For the recent (2017) PRODES raster (2007-2017 primary forests)
    # # Names for output files under each criteria. Used for both tif and shp.
    # legal_loss_year = os.path.join(utilities.out_dir, "legalAMZ_loss_{}".format(year))
    # legal_loss_year_PRODES = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_PRODES".format(year))
    # legal_loss_year_PRODES_noFire = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_PRODES_noFire".format(year))
    # legal_loss_year_PRODES_noFire_neighbor = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_PRODES_noFire_neighbor".format(year))
    # legal_loss_year_PRODES_noFire_neighbor_shp = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_PRODES_noFire_neighbor_convert.shp".format(year))
    # legal_loss_year_PRODES_noFire_neighbor_shp_dissolve = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_PRODES_noFire_neighbor_convert_diss.shp".format(year))
    # legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_PRODES_noFire_neighbor_convert_diss_reproj.shp".format(year))
    # legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj_areas = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_PRODES_noFire_neighbor_convert_diss_reproj_areas.shp".format(year))
    # legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj_areas_large = os.path.join(utilities.out_dir, "legalAMZ_loss_{}_PRODES_noFire_neighbor_convert_diss_reproj_areas_large.shp".format(year))
    #
    # # Annual PRODES primary forest extents for the 2017 PRODES raster
    # PRODES_prim = os.path.join(utilities.dir, utilities.PRODES_folder, "PRODES_primary_forest_{}.tif".format(year))

    # Masks loss in legal Amazon (criteria 1) to the given year
    print "  Masking loss to", year
    print "    Start time is", str(datetime.datetime.now())
    arcpy.gp.Con_sa("{0}/{1}".format(utilities.loss_dir, utilities.legal_Amazon_loss), "{0}/{1}".format(utilities.loss_dir, utilities.legal_Amazon_loss),
                    "{}.tif".format(legal_loss_year), "",
                    '"Value" = {}'.format(short_year))
    print "    End time is", str(datetime.datetime.now())

    # Clips loss to where there is PRODES primary forest from that year (Brazil exclusion criteria 2)
    print "  Clipping loss raster to loss in PRODES primary forest"
    print "    Start time is", str(datetime.datetime.now())
    arcpy.gp.ExtractByMask_sa("{}.tif".format(legal_loss_year),
                              PRODES_prim,
                              "{}.tif".format(legal_loss_year_PRODES))
    print "    End time is", str(datetime.datetime.now())

    # Masks loss to pixels that were not burned (Brazil exclusion criteria 3).
    # Uses a merged burn year raster instead of a raster mosaic dataset because I couldn't get Con to work on the mosaic for some reason.
    # However, I did get Con to work on a single raster of all the burn tiled merged after I create an attribute table for it,
    # so I used the merged raster instead.
    # For loss in 2001, only considers burn pixels from 2001 because considering previous year burning would include "0",
    # which means no burning was observed.
    if short_year == 1:

        print "  Removing loss pixels with fire in", year, "or", year-1
        print "    Start time is", str(datetime.datetime.now())
        arcpy.gp.Con_sa(os.path.join(utilities.dir, utilities.burnyear_merge), "{}.tif".format(legal_loss_year_PRODES),
                        "{}.tif".format(legal_loss_year_PRODES_noFire), "",
                        '"Value" NOT IN ({0})'.format(short_year))
        print "    End time is", str(datetime.datetime.now())

    # For loss in all later years (after 2001), considers burn pixels from the loss year and the preceding year.
    # Uses burn pixels from the loss year and previous year because loss could have occurred in the previous year but not been observed until the following year.
    else:

        print "  Removing loss pixels with fire in", year, "or", year-1
        print "    Start time is", str(datetime.datetime.now())
        arcpy.gp.Con_sa(os.path.join(utilities.dir, utilities.burnyear_merge), "{}.tif".format(legal_loss_year_PRODES),
                        "{}.tif".format(legal_loss_year_PRODES_noFire), "",
                        '"Value" NOT IN ({0}-1, {0})'.format(short_year))
        print "    End time is", str(datetime.datetime.now())

    # Converts the rasters created so far to shapefiles so that their areas and emissions can be calculated
    print "  Converting rasters to shapefiles..."
    arcpy.RasterToPolygon_conversion("{}.tif".format(legal_loss_year),
                                     "{}.shp".format(legal_loss_year),
                                     "NO_SIMPLIFY", "VALUE")
    arcpy.RasterToPolygon_conversion("{}.tif".format(legal_loss_year_PRODES),
                                     "{}.shp".format(legal_loss_year_PRODES),
                                     "NO_SIMPLIFY", "VALUE")

    # Checks if the non-burned loss raster actually has any data. If it doesn't (if all loss was due to burning),
    # the script moves to the next year. If there is loss not due to burning, the script continues processing this year.
    gtif = gdal.Open("{}.tif".format(legal_loss_year_PRODES_noFire))
    srcband = gtif.GetRasterBand(1)
    stats = srcband.GetStatistics(True, True)
    print "  Raster stats =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])

    if stats[2] == 0:

        print "  No non-burned loss in {}. Moving to next year.".format(year)
        # arcpy.Delete_management("{}.tif".format(legal_loss_year_PRODES_noFire))

        continue

    else:

        print "  Non-burned loss in {}. Continuing with this year.".format(year)

        # This raster is only converted to a shp if it has data in it (if there's non-burn loss)
        arcpy.RasterToPolygon_conversion("{}.tif".format(legal_loss_year_PRODES_noFire),
                                         "{}.shp".format(legal_loss_year_PRODES_noFire),
                                         "NO_SIMPLIFY", "VALUE")

        # Groups loss pixels into clusters of contiguous pixels (including diagonal pixels).
        # Each cluster gets its own ID number.
        print "  Grouping neighboring loss cells"
        print "    Start time is", str(datetime.datetime.now())
        outRegionGrp = RegionGroup("{}.tif".format(legal_loss_year_PRODES_noFire), "EIGHT", "WITHIN", "NO_LINK")
        print "Saving neighboring cells raster"
        outRegionGrp.save("{}.tif".format(legal_loss_year_PRODES_noFire_neighbor))
        print "    End time is", str(datetime.datetime.now())

        # Converts the grouped annual loss raster into a shapefile
        print "  Converting {0} loss raster to {0} loss polygon".format(year)
        print "    Start time is", str(datetime.datetime.now())
        arcpy.RasterToPolygon_conversion("{}.tif".format(legal_loss_year_PRODES_noFire_neighbor), legal_loss_year_PRODES_noFire_neighbor_shp, raster_field="Value", simplify="NO_SIMPLIFY")
        print "    Dissolving features into contiguous forest features"
        arcpy.Dissolve_management(legal_loss_year_PRODES_noFire_neighbor_shp, legal_loss_year_PRODES_noFire_neighbor_shp_dissolve, dissolve_field=["gridcode"], multi_part="MULTI_PART")
        print "    End time is", str(datetime.datetime.now())

        print "  Reprojecting {} loss area to World Eckert IV".format(year)
        print "    Start time is", str(datetime.datetime.now())
        out_coordinate_system = "PROJCS['World_Eckert_IV',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Eckert_IV'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],UNIT['Meter',1.0]]"
        arcpy.Project_management(legal_loss_year_PRODES_noFire_neighbor_shp_dissolve, legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj, out_coor_system=out_coordinate_system, transform_method="")
        print "    End time is", str(datetime.datetime.now())

        print "  Calculating feature areas"
        print "    Start time is", str(datetime.datetime.now())
        arcpy.CalculateAreas_stats(legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj, legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj_areas)
        print "    End time is", str(datetime.datetime.now())

        # Keeps only the features that are larger than 6.25 ha (Brazil exclusion criteria 4)
        print "  Selecting features larger than 6.25 ha"
        print "    Start time is", str(datetime.datetime.now())
        where = "F_AREA > 62500"
        arcpy.MakeFeatureLayer_management(legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj_areas, "layer_{}".format(year), where_clause=where)
        arcpy.CopyFeatures_management("layer_{}".format(year), legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj_areas_large)
        print "    End time is", str(datetime.datetime.now())

        # Deletes shapefiles that have the same features as a shapefile created later (redundant shapefile)
        print "  Deleting unnecessary shapefiles..."
        arcpy.Delete_management(legal_loss_year_PRODES_noFire_neighbor_shp)
        arcpy.Delete_management(legal_loss_year_PRODES_noFire_neighbor_shp_dissolve)
        arcpy.Delete_management(legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj)
        arcpy.Delete_management(legal_loss_year_PRODES_noFire_neighbor_shp_dissolve_reproj_areas)