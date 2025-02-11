import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio.windows import from_bounds
from rasterio.errors import WindowError


def align_raster(source_path, target_path, output_path):
    """
    Reads, clips, and aligns a source raster to match the dimensions and resolution of a target raster.

    Parameters:
        source_path (str): Path to the source raster.
        target_path (str): Path to the target raster.
        output_path (str): Path to save the aligned raster.

    Returns:
        numpy.ndarray: Aligned raster data matching the target's dimensions.
    """
    try:
        # Read source raster
        with rasterio.open(source_path) as src:
            source_data = src.read(1)  # Read the first band
            source_meta = src.meta.copy()

        # Read target raster
        with rasterio.open(target_path) as tgt:
            target_data = tgt.read(1)  # Read the first band
            target_meta = tgt.meta.copy()

        # Calculate the intersection of source and target bounds
        source_bounds = rasterio.windows.bounds(
            rasterio.windows.Window(0, 0, source_meta['width'], source_meta['height']),
            source_meta['transform']
        )
        target_bounds = rasterio.windows.bounds(
            rasterio.windows.Window(0, 0, target_meta['width'], target_meta['height']),
            target_meta['transform']
        )

        # Compute the intersection of the two bounding boxes
        intersect_bounds = (
            max(source_bounds[0], target_bounds[0]),  # max of min_x
            max(source_bounds[1], target_bounds[1]),  # max of min_y
            min(source_bounds[2], target_bounds[2]),  # min of max_x
            min(source_bounds[3], target_bounds[3])  # min of max_y
        )

        # Ensure the intersection is valid
        if intersect_bounds[0] >= intersect_bounds[2] or intersect_bounds[1] >= intersect_bounds[3]:
            raise ValueError("No overlapping area between source and target rasters.")

        # Clip the source raster to the intersection bounds
        window = from_bounds(*intersect_bounds, transform=source_meta['transform'])
        window = rasterio.windows.Window(
            int(window.col_off), int(window.row_off), int(window.width), int(window.height)
        )
        source_clipped = source_data[
                         window.row_off: window.row_off + window.height,
                         window.col_off: window.col_off + window.width
                         ]

        # Update metadata for the clipped raster
        clipped_transform = rasterio.windows.transform(window, source_meta['transform'])
        source_meta_clipped = source_meta.copy()
        source_meta_clipped.update({
            "height": source_clipped.shape[0],
            "width": source_clipped.shape[1],
            "transform": clipped_transform,
        })

        # Align the clipped raster to the target raster
        aligned_data = np.empty_like(target_data, dtype=np.float32)
        reproject(
            source=source_clipped,
            destination=aligned_data,
            src_transform=source_meta_clipped['transform'],
            src_crs=source_meta_clipped['crs'],
            dst_transform=target_meta['transform'],
            dst_crs=target_meta['crs'],
            resampling=Resampling.bilinear,  # Adjust resampling method as needed
        )

        # Update metadata for output raster
        aligned_meta = target_meta.copy()
        aligned_meta.update({
            "dtype": "float32",
            "nodata": 0
        })

        # Save the aligned raster
        with rasterio.open(output_path, "w", **aligned_meta) as dst:
            dst.write(aligned_data, 1)

        print(f"Aligned raster saved to: {output_path}")
        return aligned_data

    except WindowError as e:
        print(f"Error in clipping the raster: {e}")
        print("Bounds likely exceed the source raster's extent.")
        raise

    except ValueError as e:
        print(f"Error: {e}")
        raise


# source_raster = r'C:\Users\www\WRI-cif\Amsterdam\Laz_result\aoi2\aoi2_local_dem_building_utm.tif'
# target_raster = r"C:\Users\www\WRI-cif\Amsterdam\Laz_result\aoi2\aoi2_tree_32631.tif"
# output_raster = r"C:\Users\www\WRI-cif\Amsterdam\Laz_result\aoi2\aoi2_local_dem_building_utm_a.tif"
#
# align_raster(source_raster, target_raster, output_raster)

#aoi2_local_dem_building_utm


def resample_raster_to_1m(input_raster, output_raster):
    """
    Resamples a raster to a resolution of 1 meter while maintaining the original extent.

    Parameters:
        input_raster (str): Path to the input raster file.
        output_raster (str): Path to save the resampled raster with 1m resolution.
    """
    with rasterio.open(input_raster) as src:
        # Get original bounds
        xmin, ymin, xmax, ymax = src.bounds

        # Set target resolution to 1m
        target_res = 1

        # Calculate new dimensions
        width = int((xmax - xmin) / target_res)
        height = int((ymax - ymin) / target_res)

        # Define new transform
        new_transform = rasterio.transform.from_origin(xmin, ymax, target_res, target_res)

        # Read and resample the raster
        data = src.read(
            out_shape=(src.count, height, width),  # Adjust the shape
            resampling=Resampling.bilinear  # Use bilinear resampling for smooth scaling
        )

        # Write resampled raster to a new file
        with rasterio.open(
            output_raster,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=src.count,
            dtype=src.dtypes[0],
            crs=src.crs,
            transform=new_transform,
            nodata=src.nodata
        ) as dst:
            dst.write(data)

    print(f"Raster resampled to 1m resolution: {output_raster}")

# Example usage:
resample_raster_to_1m(r"C:\Users\www\WRI-cif\Amsterdam\Laz_result\aoi2\aoi2_local_dem_utm_a.tif", r"C:\Users\www\WRI-cif\Amsterdam\Laz_result\aoi2\aoi2_local_dem_utm_f.tif")
