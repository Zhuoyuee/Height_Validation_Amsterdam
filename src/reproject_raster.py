import os
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.crs import CRS
from rasterio.env import Env
import numpy as np

# **Set PROJ_LIB to ensure Rasterio finds the correct proj.db**
os.environ["PROJ_LIB"] = r"C:\Users\www\PycharmProjects\Height_Ams\venv\Lib\site-packages\rasterio\proj_data"


def force_crs(input_raster_path, output_raster_path, forced_epsg):
    """ Forcefully assigns a CRS to a raster without modifying data. """
    forced_crs = CRS.from_epsg(forced_epsg)

    with rasterio.open(input_raster_path) as src:
        kwargs = src.meta.copy()
        kwargs.update({'crs': forced_crs})  # **Force the correct CRS**

        with rasterio.open(output_raster_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                dst.write(src.read(i), i)

    print(f"CRS forced to EPSG:{forced_epsg} → {output_raster_path}")
    return output_raster_path


def transform_raster(input_raster_path, output_raster_path, src_epsg, dst_epsg):
    """ Reprojects a raster from src_epsg to dst_epsg. """

    # **First, force the CRS onto the raster to avoid EngineeringCRS issues**
    corrected_raster_path = input_raster_path.replace(".tif", "_fixed_crs.tif")
    input_raster_path = force_crs(input_raster_path, corrected_raster_path, src_epsg)

    # Print PROJ data path for verification
    print("Using PROJ data path:", os.environ["PROJ_LIB"])

    # Define CRS using EPSG codes
    src_crs = CRS.from_epsg(src_epsg)
    dst_crs = CRS.from_epsg(dst_epsg)

    with Env():
        # Open the corrected raster
        with rasterio.open(input_raster_path) as src:
            # Calculate transformation and dimensions
            transform, width, height = calculate_default_transform(
                src_crs, dst_crs, src.width, src.height, *src.bounds)

            # Update metadata
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            # Create the transformed raster
            with rasterio.open(output_raster_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    band = np.empty((height, width), dtype=src.dtypes[i - 1])

                    # Reproject each band
                    reproject(
                        source=rasterio.band(src, i),
                        destination=band,
                        src_transform=src.transform,
                        src_crs=src_crs,  # **FORCE correct CRS**
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)

                    dst.write(band, i)

    print(f"Transformation complete: {input_raster_path} → {output_raster_path}")


# Paths and EPSG codes
input_raster = r'C:\Users\www\WRI-cif\Amsterdam\Laz_result\aoi2\aoi2_local_dem.tif'
output_raster = r'C:\Users\www\WRI-cif\Amsterdam\Laz_result\aoi2\aoi2_local_dem_utm.tif'
source_crs = 28992  # Amersfoort / RD New (Force this CRS)
destination_crs = 32631  # UTM Zone 31N

transform_raster(input_raster, output_raster, source_crs, destination_crs)
