import geopandas as gpd
from rasterio.mask import mask
import rasterio
import numpy as np
import os

def align_and_crop_raster(raster_path, geojson_path, output_path=None):
    if output_path and os.path.exists(output_path):
        print(f"File {output_path} already exists. Skipping reprocessing.")
        return rasterio.open(output_path), None  # Assuming subsequent processing can handle this

    with rasterio.open(raster_path) as src:
        gdf = gpd.read_file(geojson_path)
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)

        shapes = gdf.geometry
        out_image, out_transform = mask(src, shapes, crop=True)

        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "crs": src.crs
        })

        if output_path:
            with rasterio.open(output_path, 'w', **out_meta) as dst:
                dst.write(out_image, 1)
            return rasterio.open(output_path), None

        return out_image, out_meta

def calculate_difference(gt_data, gt_meta, model_data, model_meta, difference_path):
    # Validation of shapes and transforms
    assert gt_data.shape == model_data.shape, "Ground Truth and Model data shapes must match"
    assert gt_meta['transform'] == model_meta['transform'], "Geo-transforms must match"

    # Calculate the difference
    if gt_data.ndim == 3:  # In case data includes a band dimension
        difference = gt_data.astype('float32')[0] - model_data.astype('float32')[0]
    else:
        difference = gt_data.astype('float32') - model_data.astype('float32')

    # Prepare metadata for difference output
    meta = gt_meta.copy()
    meta.update({
        'dtype': 'float32',
        'count': 1  # Ensure single band output
    })

    # Write the difference to the file
    with rasterio.open(difference_path, 'w', **meta) as dst:
        dst.write(difference, 1)


gt_path = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\DSM_AMS_m_complete.tif'
gt_resampled_output = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\DSM_AMS_m_comp_1m.tif'
model_path = r'C:\Users\zhuoyue.wang\Documents\DLmodel_Amsterdam\Amsterdam_height.tif'
model_aligned_output = r'C:\Users\zhuoyue.wang\Documents\DLmodel_Amsterdam\Ams_DLheight_a.tif'

amsterdam_geojson = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\Boundary_AMS.GeoJSON'
overture_buildings_geojson = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\Amsterdam_overturebuildings.geojson'
difference_path = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\diff_gt-dl.tif'

gt_resampled = r'C:\Users\zhuoyue.wang\Documents\DLmodel_Amsterdam\Ams_DLheight_a.tif'
model_aligned = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\DSM_AMS_m_comp_1m.tif'

# Crop both layers by Amsterdam boundary and then by overture buildings
gt_cropped_data1, gt_cropped_meta = align_and_crop_raster(gt_resampled, amsterdam_geojson)
model_cropped_data1, model_cropped_meta = align_and_crop_raster(model_aligned, amsterdam_geojson)

gt_cropped_data2, gt_cropped_meta1 = align_and_crop_raster(gt_resampled, overture_buildings_geojson)
model_cropped_data2, model_cropped_meta1 = align_and_crop_raster(model_aligned, overture_buildings_geojson)

calculate_difference(gt_cropped_data2, gt_cropped_meta, model_cropped_data2, model_cropped_meta, difference_path)