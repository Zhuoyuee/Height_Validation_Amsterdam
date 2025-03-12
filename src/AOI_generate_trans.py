import geopandas as gpd
from pyproj import CRS, Transformer


def reproject_geopackage(input_geopackage, output_geopackage, target_crs="EPSG:28992"):
    """
    Reprojects a GeoPackage to a target CRS and optionally writes the output to a file.

    Parameters:
    - input_geopackage (str): Path to the input GeoPackage.
    - output_geopackage (str, optional): Path to save the reprojected GeoPackage. Default is None (no file written).
    - target_crs (str): Target CRS in EPSG format. Default is "EPSG:28992".

    Returns:
    - gpd.GeoDataFrame: Reprojected GeoDataFrame.
    """
    # Read the input GeoPackage
    gdf = gpd.read_file(input_geopackage)

    if gdf.empty:
        raise ValueError("The input GeoPackage is empty or invalid.")

    # Print the original CRS and bounding box
    print("Original CRS:", gdf.crs)
    print("Original Bounding Box:", gdf.total_bounds)

    # Create a transformer to calculate the new bounding box in the target CRS
    transformer = Transformer.from_crs(gdf.crs, target_crs, always_xy=True)
    bbx_original = gdf.total_bounds  # [minx, miny, maxx, maxy]

    # Transform the bounding box coordinates
    minx, miny = transformer.transform(bbx_original[0], bbx_original[1])
    maxx, maxy = transformer.transform(bbx_original[2], bbx_original[3])
    transformed_bbox = [minx, miny, maxx, maxy]

    # Reproject the GeoDataFrame to the target CRS
    gdf_reprojected = gdf.to_crs(target_crs)

    # Print the transformed CRS and bounding box
    print("Target CRS:", target_crs)
    print("Transformed Bounding Box:", transformed_bbox)

    # Save the reprojected GeoPackage if an output path is provided
    if output_geopackage:
        gdf_reprojected.to_file(output_geopackage, driver="GPKG")
        print(f"Reprojected GeoPackage saved to {output_geopackage}")

    return gdf_reprojected

reproject_geopackage(r'C:\Users\www\WRI-cif\AOI_2_utm.gpkg', r'C:\Users\www\WRI-cif\aoi2_28992.gpkg', target_crs="EPSG:28992")
# [120764.45790837877, 485845.9530135797, 122764.4639352827, 487845.9552846286]