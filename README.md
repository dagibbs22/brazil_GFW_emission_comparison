This script applies the same criteria that Brazil uses for calculating its annual Amazon deforestation statistics to the UMD/Hansen loss.
The criteria are that loss must be: 1) within the legal Amazon, 2) within PRODES primary forest for that year, 4) without fire that year or the preceding year, and 4) in a cluster greater than 6.25 ha.
Applying these criteria to annual Hansen loss allows for more direct comparison of loss area and resulting emissions with Brazil's official statistics than a direct comparison.

Run Brazil_GFW_emissions_comparison.py on a local computer. 
This requires ArcPy and several input files: Hansen annual loss tiles for the legal Amazon, annual burned area tiles, PRODES primary forest extent for each year of analysis, and a legal Amazon boundary shapefile.
As each criterion is applied, a new tif and shapefile are created. The creation of a shapefile following the application of each criterion means that the effect on loss and emissions of each criterion can be examined.
For example, how much does restricting loss to areas that did not burn affect the loss/emissions total?
This can take a few hours to run for each year of loss analyzed.

Copy the outputs (tifs and shapefiles) to s3.

After shapefiles for all years are created, the next step is to create a field with in each shapefile with the filename. This is done with prep_for_tsv_creation.py.
This field with the name of the file will be used in Hadoop to identify the which shapefile the results are for.

The next step is to convert the shapefiles to tsvs without intersecting them with administrative boundaries (GADM). This project does not require knowing the loss/emissions by administrative region.
This can be done with convert-AOI-to-tsv.py in https://github.com/wri/gfw-annual-loss-processing.

Finally, the tsvs are put through Hadoop ()https://github.com/wri/gfw-annual-loss-processing/tree/master/1c_Hadoop-Processing) and post-processed (https://github.com/wri/gfw-annual-loss-processing/blob/master/2_Cumulate-Results-and-Create-API-Datasets/cumsum_hadoop_output.py).
