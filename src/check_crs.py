import geopandas as gpd

# Read the GeoPackage (automatically loads the first/only layer if no layer is specified)
gdf_3035 = gpd.read_file(r'C:\Users\www\WRI-cif\v0_1-NLD_9_4_1-Amsterdam.gpkg')

# Confirm current CRS
print("Original CRS:", gdf_3035.crs)

# Reproject to EPSG:28992
gdf_28992 = gdf_3035.to_crs(epsg=28992)

# Save the reprojected file
gdf_28992.to_file(r'C:\Users\www\WRI-cif\py_Eubucco_28992.gpkg', driver='GPKG')