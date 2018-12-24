Run Brazil_GFW_emissions_somparison.py on a local computer. 
Requires ArcPy and several input files, such as Hansen loss tiles, burned area tiles, PRODES primary forest extent, and legal Amazon shapefile.
Outputs a series of tifs and shapefiles for each loss year it iterates across.
This can take several hours to run for each year of loss analyzed.

Copy the outputs (tifs and shapefiles) to s3.

After shapefiles for all years are created, the next step is to combine them, intersect them with GADM, and convert them to tsvs.
This is done on a spot machine because there are so many giant shapefiles involved.
Create an m4.16xlarge spot machine.

Copy shapefiles for one year (2001) to a spot machine. Good for testing.
`aws s3 cp s3://gfw-files/dgibbs/GFW_Climate/Brazil_emis_comparison/full_model_201810/output/ . --recursive --exclude "*" --include "*2001*.shp" --include "*2001*.prj" --include "*2001*.cpg" --include "*2001*.dbf" --include "*2001*.sbn" --include "*2001*.sbx" --include "*2001*.shx" --exclude "*tif*"`

Copy all shapefiles to a spot machine
`aws s3 cp s3://gfw-files/dgibbs/GFW_Climate/Brazil_emis_comparison/full_model_201810/output/ . --recursive --exclude "*" --include "*.shp" --include "*prj" --include "*.cpg" --include "*.dbf" --include "*.sbn" --include "*.sbx" --include "*.shx" --exclude "*tif*"`

Remove the redundant shapefiles from the spot machine (those with the same features). (This could be done in the cp command but I didn't think of that, so I made it a separate step)
`rm *PRODES_neighbor_convert.*`
`rm *convert_diss.*`
`rm *convert_diss_reproj.*`

Load one shapefile into a PostGIS database
`ogr2ogr -f Postgresql PG:"dbname=ubuntu" loss_2001_early.shp -progress -nln merged -sql "SELECT name FROM loss_2001_early"`

Enter the psql shell: `psql`

Check that all the rows for that table were imported:
`SELECT COUNT (*) FROM merged;`

Delete the data just added to the table but keep the table. This way, you have an empty table and can add all the shapefiles on the spot machine to it.
`DELETE FROM merged;`

Change the geometry of the table to multipolygon
`ALTER TABLE merged ALTER COLUMN wkb_geometry type geometry(MultiPolygon, 102689) using ST_Multi(wkb_geometry);`

Exit the psql shell.
`ctrl + z`

Iterate through all the shapefiles on the spot machine to add them to the PostGIS table. This does not work with a sql statement selecting columns but it appears that only the columns imported in the initial table creation step are actually imported.
It is based on this post: https://gis.stackexchange.com/questions/136553/batch-load-multiple-shapefiles-to-postgis
`for shp in $(ls *.shp); do echo $shp; ogr2ogr -f "PostgreSQL" PG:"dbname=ubuntu" -append -nln merged -nlt MULTIPOLYGON -progress $shp; done;`

Clone the gfw-annual-loss-processing repo:
`git clone https://github.com/wri/gfw-annual-loss-processing`

Follow the directions there for intersecting tsvs with gadm. The command I used for this was:
`python intersect-source-with-gadm.py --input-dataset merged --zip-source s3://gfw2-data/alerts-tsv/gis_source/gadm_3_6_adm2_final.zip --output-name PRODES_comparison --s3-out-dir s3://gfw-files/dgibbs/GFW_Climate/Brazil_emis_comparison/full_model_201810/tsvs_for_Hadoop_20181224/`
