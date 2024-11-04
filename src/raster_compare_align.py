import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np


def resample_raster(input_path, output_path, new_resolution=(1, 1)):
    with rasterio.open(input_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, src.crs, src.width, src.height, *src.bounds, resolution=new_resolution
        )

        # Set up metadata for the output file
        kwargs = src.meta.copy()
        kwargs.update({
            'driver': 'GTiff',
            'height': height,
            'width': width,
            'transform': transform,
            'crs': src.crs
        })

        data = src.read(
            out_shape=(src.count, height, width),
            resampling=Resampling.bilinear
        )

        # with rasterio.open(output_path, 'w', **kwargs) as dst:
        #     dst.write(data)

    return data, kwargs


def align_data(model_path, reference_meta, aligned_model_path):
    with rasterio.open(model_path) as model:
        data_type = 'float32'  # Ensuring we're using a flexible data type
        aligned_model = np.empty((model.count, reference_meta['height'], reference_meta['width']), dtype=data_type)

        reproject(
            source=rasterio.band(model, 1),
            destination=aligned_model[0],  # Target the first band explicitly
            src_transform=model.transform,
            src_crs=model.crs,
            dst_transform=reference_meta['transform'],
            dst_crs=reference_meta['crs'],
            resampling=Resampling.bilinear,
            src_nodata=model.nodata,
            dst_nodata=-9999  # Make sure this is appropriate for the data type
        )

        # Update metadata for output, ensuring it matches the expectations
        output_meta = reference_meta.copy()
        output_meta.update({
            'driver': 'GTiff',
            'height': reference_meta['height'],
            'width': reference_meta['width'],
            'transform': reference_meta['transform'],
            'crs': reference_meta['crs'],
            'dtype': data_type,
            'nodata': -9999
        })

        # Write the aligned data, ensuring we only pass a 2D array for each band
        with rasterio.open(aligned_model_path, 'w', **output_meta) as dst:
            dst.write(aligned_model[0], 1)  # Write the first band

    return aligned_model, output_meta

# gt_resampled, gt_meta = resample_raster(gt_path, gt_resampled_output)
#
# # Align model data to the ground truth
# model_aligned, model_meta = align_data(model_path, gt_meta, model_aligned_output)