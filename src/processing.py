import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds
from shapely.geometry import Point, box
from rtree import index
import numpy as np

# Define the Stats class to store statistics
class Stats:
    def __init__(self, max_val, min_val, avg_val, stddev_val, num_points, avg_diff):
        self.max_val = max_val
        self.min_val = min_val
        self.avg_val = avg_val
        self.stddev_val = stddev_val
        self.num_points = num_points
        self.avg_diff = avg_diff  # Difference between average cell height and building height

    def __str__(self):
        return (f"Max: {self.max_val}, Min: {self.min_val}, Avg: {self.avg_val}, "
                f"Stddev: {self.stddev_val}, Points: {self.num_points}, Avg Diff: {self.avg_diff}")

# Function to calculate statistics for cell heights inside a polygon
def calculate_height_stats(cell_heights, building_height):
    avg_height = np.mean(cell_heights)
    stats = Stats(
        max_val=np.max(cell_heights),
        min_val=np.min(cell_heights),
        avg_val=avg_height,
        stddev_val=np.std(cell_heights),
        num_points=len(cell_heights),
        avg_diff=avg_height - building_height  # Difference between avg height of cells and building height
    )
    return stats

# Function to find points inside a polygon using R-tree spatial index
def points_in_polygon(polygon, cell_centers_and_heights, spatial_idx):
    candidates = list(spatial_idx.intersection(polygon.bounds))  # Get candidate points by bounding box
    points_within_polygon = [(cell_centers_and_heights[i][0], cell_centers_and_heights[i][1]) for i in candidates if polygon.contains(cell_centers_and_heights[i][0])]  # Exact check
    return points_within_polygon

# Function to process each building and calculate statistics for points inside the polygon
def process_buildings(cropped_raster_data, cropped_vector_data, transform):
    # Generate cell centers and heights from the cropped raster
    cell_centers_and_heights = generate_cell_centers_and_heights(cropped_raster_data, transform)

    # Build the spatial index for all cell centers
    spatial_idx = build_spatial_index(cell_centers_and_heights)

    # Store building stats in a dictionary
    building_stats = {}

    # Lists to store differences for overall performance
    all_diffs = []

    # Loop through each building polygon in the vector file
    for idx, building in cropped_vector_data.iterrows():
        building_polygon = building.geometry
        building_height = building['height']  # Assuming 'height' is the column name

        # Find the cell centers inside the building polygon
        points_in_poly = points_in_polygon(building_polygon, cell_centers_and_heights, spatial_idx)

        # Collect heights for the points within the polygon
        cell_heights = [height for point, height in points_in_poly]

        # Calculate stats if there are any points in the polygon
        if cell_heights:
            stats = calculate_height_stats(cell_heights, building_height)
            building_stats[building['id']] = stats  # Use building ID as key

            # Append the difference to the overall performance list
            all_diffs.append(stats.avg_diff)

    # Calculate overall performance
    avg_diff = np.mean(all_diffs) if all_diffs else 0
    stddev_diff = np.std(all_diffs) if all_diffs else 0

    return building_stats, avg_diff, stddev_diff