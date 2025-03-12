import geopandas as gpd


def reproject_layer(input_path, output_path, target_crs="EPSG:32631"):
    """
    Reprojects a GeoDataFrame to a specified CRS and handles specific attribute adjustments.

    Parameters:
        input_path (str): Path to the input GeoJSON or GPKG file.
        output_path (str): Path to save the reprojected layer.
        target_crs (str): The EPSG code of the target CRS.
    """
    # Load the GeoDataFrame
    gdf = gpd.read_file(input_path)

    # Inspect the 'sources' column; modify it if necessary
    if 'sources' in gdf.columns:
        print("Original 'sources' type:", gdf['sources'].dtype)
        # Assuming 'sources' should be a string or None if it's problematic
        gdf['sources'] = gdf['sources'].apply(lambda x: str(x) if x else None)

    # Reproject the GeoDataFrame
    gdf = gdf.to_crs(target_crs)

    # Save the reprojected GeoDataFrame
    gdf.to_file(output_path, driver='GeoJSON')  # Adjust the driver based on your file format

    print(f"Layer has been reprojected and saved to {output_path}.")


# Example usage
reproject_layer(r"C:\Users\zhuoyue.wang\Documents\Amsterdam_data\Height_validation\ams_overture_height_reproj1.geojson", r"C:\Users\zhuoyue.wang\Documents\Amsterdam_data\Height_validation\aoi1_overture_height_utm1.geojson")
