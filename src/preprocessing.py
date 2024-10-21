import rasterio
from rasterio.windows import from_bounds

# Function to crop raster array data based on bounds without filling missing areas
def crop_raster(raster_data, transform, minx, miny, maxx, maxy):
    # Create a window from the bounding box
    window = from_bounds(minx, miny, maxx, maxy, transform=transform)

    # Crop the data using the calculated window bounds
    row_start = max(0, int(window.row_off))
    row_stop = min(raster_data.shape[0], int(window.row_off + window.height))
    col_start = max(0, int(window.col_off))
    col_stop = min(raster_data.shape[1], int(window.col_off + window.width))

    # Crop the data
    cropped_data = raster_data[row_start:row_stop, col_start:col_stop]

    # Adjust the transform for the cropped window
    cropped_transform = rasterio.windows.transform(window, transform)

    return cropped_data, cropped_transform

# Main function to crop the rasters based on center point and buffer size
def preprocess_rasters(updated_raster, original_raster, output_cropped_before,
                       output_cropped_after, center_x, center_y, buffer_size):
    # Step 1: Define the bounding box based on the center point and buffer
    minx = center_x - buffer_size
    maxx = center_x + buffer_size
    miny = center_y - buffer_size
    maxy = center_y + buffer_size

    # Step 2: Crop the original raster to the bounding box
    with rasterio.open(original_raster) as original_src:
        original_data = original_src.read(1)
        cropped_before, cropped_before_transform = crop_raster(
            original_data, original_src.transform, minx, miny, maxx, maxy
        )

        # Update the metadata and save the cropped original raster
        meta_before = original_src.meta.copy()
        meta_before.update({
            "height": cropped_before.shape[0],
            "width": cropped_before.shape[1],
            "transform": cropped_before_transform
        })

        with rasterio.open(output_cropped_before, 'w', **meta_before) as dst_before:
            dst_before.write(cropped_before, 1)

    # Step 3: Crop the updated raster (no resampling needed) to the bounding box
    with rasterio.open(updated_raster) as updated_src:
        updated_data = updated_src.read(1)
        cropped_after, cropped_after_transform = crop_raster(
            updated_data, updated_src.transform, minx, miny, maxx, maxy
        )

        # Update the metadata and save the cropped updated raster
        meta_after = updated_src.meta.copy()
        meta_after.update({
            "height": cropped_after.shape[0],
            "width": cropped_after.shape[1],
            "transform": cropped_after_transform
        })

        with rasterio.open(output_cropped_after, 'w', **meta_after) as dst_after:
            dst_after.write(cropped_after, 1)

    print(f"Cropping complete: {output_cropped_before}, {output_cropped_after}")

# Example usage
updated_raster = r"C:\Users\www\Bee\upd_nt_m_nodata.tif"  # Updated raster
original_raster = r"C:\Users\www\Bee\ori_nt_m_nodata.tif"  # Original raster
output_cropped_before = r"C:\Users\www\Bee\Ori_nt_c1.tif"  # Cropped original raster
output_cropped_after = r"C:\Users\www\Bee\Upd_nt_c1.tif"  # Cropped updated raster

center_x, center_y = 122822.2163, 506839.2538  # Center point (EPSG:28992)
buffer_size = 3000  # 3 km buffer

# Run the preprocessing
preprocess_rasters(updated_raster, original_raster, output_cropped_before,
                   output_cropped_after, center_x, center_y, buffer_size)
