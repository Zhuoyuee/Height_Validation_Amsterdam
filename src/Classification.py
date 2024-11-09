import laspy
import numpy as np
import rasterio
from rasterio.transform import from_origin

file_path = input('File path to the cropped las file: ')

with laspy.open(file_path) as file:
    las = file.read()

class_1_points = las.points[las.classification == 1]

# Calculate NDVI for class 1 points if NIR and Red bands are available
if hasattr(las, 'red') and hasattr(las, 'nir'):
    red = class_1_points['red'].astype(float)
    nir = class_1_points['nir'].astype(float)

    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir - red) / (nir + red)
        ndvi[(nir + red) == 0] = 0  # Set NDVI to zero where red + nir is zero
    ndvi = np.clip(ndvi, -1, 1)

    # Filtering the points with the NDVI threshold
    vegetation_mask = ndvi >= 0.35

    # Filter out first return points from class 1 points
    first_return_mask_class_1 = class_1_points['return_number'] == 1

    # Combine NDVI and first return masks
    combined_mask = vegetation_mask & first_return_mask_class_1

    # Apply combined mask to class 1 points
    filtered_points = class_1_points[combined_mask]

min_x, min_y, max_x, max_y = 181437.246002, 318805.419006, 181937.246002, 319305.419006
cell_size = 1

# Grid dimensions
x_coords = np.arange(min_x, max_x, cell_size)
y_coords = np.arange(min_y, max_y, cell_size)
grid_width = len(x_coords)
grid_height = len(y_coords)

def generate_points_around(center_x, center_y, center_z, radius, num_points=10):
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    return [(center_x + radius * np.cos(angle), center_y + radius * np.sin(angle), center_z) for angle in angles]

# densifying the point cloud
radius = 0.20
densified_points = []

for x, y, z in zip(filtered_points.x, filtered_points.y, filtered_points.z):
    points_around = generate_points_around(x, y, z, radius)
    densified_points.extend(points_around)


heights = np.full((grid_height, grid_width), fill_value=np.nan, dtype=np.float64)
for x, y, z in densified_points:
    x_idx = int((x - min_x) / cell_size)
    y_idx = int((max_y - y) / cell_size)
    if 0 <= x_idx < grid_width and 0 <= y_idx < grid_height:
        if np.isnan(heights[y_idx][x_idx]) or heights[y_idx, x_idx] < z:
            heights[y_idx][x_idx] = z


# Geospatial transform
transform = from_origin(min_x, max_y, cell_size, cell_size)

# Write to a TIFF file
output_file_path = input("Enter the output file path for the vegetation raster: ")

with rasterio.open(
    output_file_path,  # Use the user-provided file path
    'w',
    driver='GTiff',
    height=heights.shape[0],
    width=heights.shape[1],
    count=1,
    dtype=heights.dtype,
    crs='EPSG:7415',  # Setting the CRS to RDNAP
    transform=transform
) as dst:
    dst.write(heights, 1)

print(f"vegetation raster saved to: {output_file_path}")



