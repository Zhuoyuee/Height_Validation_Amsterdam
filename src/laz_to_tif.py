import laspy
import numpy as np
import rasterio
from rasterio.transform import from_origin


def process_las_to_tif(las_file_path, output_tif_path, bbox, classifications=[2, 6], resolution=1):
    # Read the LAS file
    with laspy.open(las_file_path) as lasfile:
        las = lasfile.read()

        # Filter points within the bounding box and by classification
        mask_bbox = (
                (las.x >= bbox[0]) & (las.x <= bbox[2]) &
                (las.y >= bbox[1]) & (las.y <= bbox[3])
        )
        mask_class = np.isin(las.classification, classifications)
        filtered_points = las[mask_bbox & mask_class]

        # Calculate the bounds of the filtered point cloud for raster dimensions
        min_x, max_x = np.min(filtered_points.x), np.max(filtered_points.x)
        min_y, max_y = np.min(filtered_points.y), np.max(filtered_points.y)

        # Define the raster size
        width = int((max_x - min_x) // resolution + 1)
        height = int((max_y - min_y) // resolution + 1)

        # Create an array to hold the maximum elevation data
        grid = np.full((height, width), -np.inf, dtype=np.float32)

        # Populate the grid
        for x, y, z in zip(filtered_points.x, filtered_points.y, filtered_points.z):
            col = int((x - min_x) // resolution)
            row = int((y - min_y) // resolution)
            grid[row, col] = max(grid[row, col], z)

        # Create a new raster file with the specified resolution and CRS
        transform = from_origin(min_x, max_y, resolution, resolution)
        with rasterio.open(
                output_tif_path, 'w', driver='GTiff',
                height=height, width=width,
                count=1, dtype=str(grid.dtype),
                crs='EPSG:28992',
                transform=transform
        ) as dst:
            dst.write(grid, 1)


# Example usage
las_file_path = 'path/to/your/file.las'
output_tif_path = 'path/to/your/output.tif'
bbox = [120764.46, 483845.95, 122764.46, 485845.95]  # [xmin, ymin, xmax, ymax]

process_las_to_tif(las_file_path, output_tif_path, bbox)