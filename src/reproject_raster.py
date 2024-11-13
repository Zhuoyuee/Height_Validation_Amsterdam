import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pyproj import CRS

def transform_raster(input_raster_path, output_raster_path, src_epsg, dst_epsg):
    # Get CRS from EPSG using pyproj and convert to WKT
    src_crs = CRS.from_epsg(src_epsg).to_wkt()
    dst_crs = CRS.from_epsg(dst_epsg).to_wkt()

    # Open the source raster with the defined source CRS
    with rasterio.open(input_raster_path, crs=src_crs) as src:
        # Calculate the transformation and dimensions for the new raster
        transform, width, height = calculate_default_transform(
            CRS.from_wkt(src_crs), CRS.from_wkt(dst_crs), src.width, src.height, *src.bounds)

        # Define metadata for the new raster
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        # Create and write the transformed raster
        with rasterio.open(output_raster_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                # Reproject each band using the specified WKT CRS
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)


input_raster = r'C:\Users\www\WRI-cif\Amsterdam\tree_height_local.tif'
output_raster = r'C:\Users\www\WRI-cif\Amsterdam\tree_height_local_utm.tif'
source_crs = 28992
destination_crs = 32631

transform_raster(input_raster, output_raster, source_crs, destination_crs)
