import os
import arcpy
from arcpy.sa import *
import datetime

path = 'C:\GIS\GFW_Climate\Brazil_emis_comparison'

os.chdir(path)

arcpy.CheckOutExtension("Spatial")

dir = "C:\\GIS\\GFW_Climate\\Brazil_emis_comparison"

out_dir = os.path.join(dir, "output")

gdb = "loss_mosaics"
Hansen_mosaic = "Hansen_loss_2017"
burn_mosaic = "burn_loss_from_s3"
gdb_path = os.path.join(dir, gdb)
Hansen_loss_tile_path = os.path.join(dir, Hansen_mosaic)
fire_loss_tile_path = os.path.join(dir, burn_mosaic)
loss_tile = "C:\\GIS\\GFW_Climate\\Brazil_emis_comparison\\Hansen_loss_2017\\00N_050W.tif"
PRODES_folder = "PRODES"

loss_dir = "C:\\GIS\\GFW_Climate\\Brazil_emis_comparison\\Hansen_loss_2017"
legal_Amazon_loss = "loss_clipped_to_legal_Amazon_20181228.tif"
legal_Amazon_loss_dir =  os.path.join(loss_dir, legal_Amazon_loss)

# The name of the burn year tiles merged into a single raster.
# I needed to create the attribute table for this to work in the Con tool.
burnyear_merge = "burnyear_merge_20181013.tif"

# Legal Amazon boundary
legal_Amazon_reproj = "C:\\GIS\\Multi_project\\Brazil_legal_Amazon\\prodes_full_extent_reproj_align.tif"

# PRODES primary forest 2000-2013, reprojected to Hansen projection and snapped to Hansen raster
prim_2000_13 = os.path.join(dir, PRODES_folder, "Prodes2014_AMZ_60m_warp.tif")

# PRODES primary forest 2007-2017, reprojected to Hansen projection and snapped to Hansen raster
prim_2007_17 = os.path.join(dir, PRODES_folder, "PDigital2017_AMZ_30m_warp.tif")


def create_mosaics():

    print "Creating geodatabase for loss and fire mosaics in Amazonia..."
    out_coor_system = arcpy.Describe(loss_tile).spatialReference
    print "  Creating gdb..."
    arcpy.CreateFileGDB_management(dir, gdb)

    print "  Creating Hansen loss mosaic..."
    arcpy.CreateMosaicDataset_management("{}.gdb".format(gdb_path), Hansen_mosaic, out_coor_system, num_bands="1",
                                         pixel_type="8_BIT_UNSIGNED")
    print "  Adding Hansen loss tiles to mosaic..."
    arcpy.AddRastersToMosaicDataset_management("{0}.gdb/{1}".format(gdb_path, Hansen_mosaic),
                                               raster_type="Raster Dataset", input_path=Hansen_loss_tile_path)

    # I haven't actually tested this code out. It's based on the Python snippet from manually clipping, so it might
    # not work as I've modified it here. At least, the rectangle arguments need to change.
    print "  Clipping Hansen loss to Brazil boundary..."
    arcpy.Clip_management(in_raster="{0}.gdb/{1}".format(gdb_path, Hansen_mosaic),
                          rectangle="-73.9783164486978 -18.0406669808439 -43.9135843925793 5.27136996674568",
                          out_raster=legal_Amazon_loss_dir,
                          in_template_dataset="prodes_full_extent_reproj", nodata_value="256",
                          clipping_geometry="ClippingGeometry", maintain_clipping_extent="NO_MAINTAIN_EXTENT")

    # # I couldn't get the burn year mosaic to work with the Con tool (kept making error 001464 or something), so
    # # this program never actually used the burn year mosaic. Hence, left this in but commented it out.
    # print "  Creating fire loss mosaic..."
    # arcpy.CreateMosaicDataset_management("{}.gdb".format(gdb_path), burn_mosaic, out_coor_system, num_bands="1",
    #                                      pixel_type="8_BIT_UNSIGNED")
    # print "  Adding fire loss tiles to mosaic..."
    # arcpy.AddRastersToMosaicDataset_management("{0}.gdb/{1}".format(gdb_path, burn_mosaic),
    #                                            raster_type="Raster Dataset", input_path=fire_loss_tile_path)


# Iterates through 2001-2013 to create PRODES primary forest rasters
def create_annual_PRODES_early():

    # The years included in the most recent PRODES update
    for year in range(2001, 2014):

        print "Masking PRODES primary forest raster to what was there just before", year

        # Annual PRODES primary forest extents
        prim_reclass = os.path.join(dir, PRODES_folder, "PRODES_primary_forest_{}_early.tif".format(year))

        short_year = year - 2000

        print "  Start time is", str(datetime.datetime.now())
        outReclass = Reclassify(prim_2000_13, "Value",
                                RemapRange([[1, 1, short_year],
                                            [2, short_year - 2, "NODATA"], [short_year - 1, 16, short_year],
                                            [17, short_year + 6, "NODATA"], [short_year + 7, 24, short_year]]))
        print "  Saving reclassified primary forest raster"
        outReclass.save(prim_reclass)
        print "  End time is", str(datetime.datetime.now())

# Iterates through 2007-2017 to create PRODES primary forest rasters
def create_annual_PRODES_recent():

    # The years included in the most recent PRODES update
    for year in range(2007, 2018):

        print "Masking PRODES primary forest raster to what was there just before", year

        # Annual PRODES primary forest extents
        prim_reclass = os.path.join(dir, PRODES_folder, "PRODES_primary_forest_{}.tif".format(year))

        short_year = year - 2000

        # For 2007-2009, there is no residual deforestation class (r), so the reclassification rules are simpler.
        # Deforestation is the classes before the focal year (e.g., deforestation to make PRODES 2009 layer is
        # deforestation in 2007 and 2008 but not 2009).
        if short_year < 10:

            print "  PRODES before 2010"
            print "  Start time is", str(datetime.datetime.now())
            outReclass = Reclassify(prim_2007_17, "Value",
                                    RemapRange([[1, 1, short_year],
                                                [2, short_year - 2, "NODATA"], [short_year - 1, 24, short_year]]))
            print "  Saving reclassified primary forest raster"
            outReclass.save(prim_reclass)
            print "  End time is", str(datetime.datetime.now())

        # For 2010 and later, there are annual residual deforestation classes (rxxxx), so the reclassification needs to
        # account for those
        if short_year >= 10:

            print "  PRODES from 2010 or later"
            print "  Start time is", str(datetime.datetime.now())
            outReclass = Reclassify(prim_2007_17, "Value",
                                    RemapRange([[1, 1, short_year],
                                                [2, short_year - 2, "NODATA"], [short_year - 1, 16, short_year],
                                                [17, short_year + 6, "NODATA"], [short_year + 7, 24, short_year]]))
            print "  Saving reclassified primary forest raster"
            outReclass.save(prim_reclass)
            print "  End time is", str(datetime.datetime.now())