import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, Point
import logging
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(raster_path, vector_path):
    logging.info("Loading datasets...")
    raster = rasterio.open(raster_path)
    vector = gpd.read_file(vector_path)
    logging.info(f"Raster CRS: {raster.crs}, Vector CRS: {vector.crs}")
    return raster, vector


def raster_to_points(raster):
    logging.info("Converting raster to points...")
    mask = raster.read_masks(1)  # Assuming height data is in the first band

    # Read the first band of the raster
    raster_data = raster.read(1)

    # Optionally, print or log some of the raster data to see what's being read
    logging.debug(f"Raster data sample (first 10 values): {raster_data.flatten()[:10]}")

    points = []
    for (geom, value) in shapes(raster_data, mask=mask, transform=raster.transform):
        # Convert shapes to Point objects only if value is valid
        if np.isfinite(value):  # This checks for valid numerical values
            coords = geom['coordinates'][0]  # Get the first tuple of coordinates from the geometry
            try:
                # Create a Point from coordinates, ensuring they are floats
                point = Point(float(coords[0]), float(coords[1]))
                points.append((point, value))
            except ValueError as e:
                logging.error(f"Error converting coordinates to Point: {coords} with error {e}")

    logging.info(f"Generated {len(points)} points from the raster.")
    return points


def check_intersections(raster_points, buildings):
    logging.info("Checking intersections...")
    intersections = []
    for point in raster_points:
        intersected_buildings = buildings[buildings.geometry.contains(point)]
        if not intersected_buildings.empty:
            intersections.append((point, intersected_buildings))
    logging.info(f"Found intersections with {len(intersections)} points.")
    return intersections


def main(raster_path, vector_path):
    raster, buildings = load_data(raster_path, vector_path)

    if raster.crs != buildings.crs:
        logging.warning("CRS mismatch detected, reprojecting vector data...")
        buildings = buildings.to_crs(raster.crs)

    raster_points = raster_to_points(raster)
    intersections = check_intersections(raster_points, buildings)

    if not intersections:
        logging.warning("No intersections found. Check data alignment and accuracy.")
    else:
        logging.info(f"Intersections detected: {len(intersections)} points intersect with buildings.")


# Specify the paths to your raster and vector data
raster_path = r'C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey/Mon_buildingdsm.tif'
vector_path = r"C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey\mty_overture_height1.geojson"

main(raster_path, vector_path)
