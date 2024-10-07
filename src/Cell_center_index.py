import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds
from shapely.geometry import Point, box
from rtree import index
import numpy as np

# Updated: Function to generate the center points and height values of each raster cell
def generate_cell_centers_and_heights(cropped_data, transform):
    raster_height, raster_width = cropped_data.shape
    cell_centers_and_heights = []

    # Loop over the rows and columns of the raster to get the center points and heights
    for row in range(raster_height):
        for col in range(raster_width):
            x, y = rasterio.transform.xy(transform, row, col, offset='center')
            height = cropped_data[row, col]  # Get the height value from the raster
            cell_centers_and_heights.append((Point(x, y), height))  # Store center point and height

    return cell_centers_and_heights

# Function to build an R-tree spatial index for fast lookups
def build_spatial_index(cell_centers_and_heights):
    idx = index.Index()
    for i, (point, height) in enumerate(cell_centers_and_heights):
        idx.insert(i, (point.x, point.y, point.x, point.y))  # Insert point's bounding box into the index
    return idx