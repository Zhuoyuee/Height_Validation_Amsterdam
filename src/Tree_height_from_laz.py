import laspy
import numpy as np
from sklearn.cluster import DBSCAN

def filter_tree_canopy(input_path, output_path, bbx,
                       min_height=2.0, min_cluster_area=5, ndvi_threshold=0.2,
                       eps=1.5, min_samples=5, point_density=1.5):
    """
    Filters and saves vegetation points representing tree canopies from a LAZ file.

    Parameters:
    - input_path: Path to the input LAZ file.
    - output_path: Path where the filtered LAZ file will be saved.
    - bbx: Bounding box as a tuple (min_x, max_x, min_y, max_y).
    - min_height: Minimum height threshold to exclude low vegetation and ground objects.
    - min_cluster_area: Minimum area threshold for clusters to be considered tree canopies.
    - ndvi_threshold: NDVI threshold for vegetation filtering (if NDVI is available).
    - eps: DBSCAN epsilon value for clustering in meters.
    - min_samples: Minimum samples for DBSCAN clustering.
    - point_density: Estimated points per square meter to determine cluster size.
    """
    # Unpack bounding box
    min_x, max_x, min_y, max_y = bbx

    # Load the LAZ file
    las = laspy.read(input_path)

    # Step 1: Crop by Bounding Box (BBX)
    x_filter = (las.x >= min_x) & (las.x <= max_x)
    y_filter = (las.y >= min_y) & (las.y <= max_y)
    bbx_filtered = las.points[x_filter & y_filter]

    # Step 2: Filter for Unclassified Points (Class 1)
    unclassified_filter = (bbx_filtered['classification'] == 1)
    unclassified_points = bbx_filtered[unclassified_filter]

    # Step 3: Apply NDVI Threshold if Red and NIR bands are available
    if hasattr(unclassified_points, 'Red') and hasattr(unclassified_points, 'NIR'):
        red = unclassified_points['Red']
        nir = unclassified_points['NIR']
        ndvi = (nir - red) / (nir + red)
        ndvi_filter = ndvi > ndvi_threshold
    else:
        print("NDVI data not available in point cloud.")
        ndvi_filter = np.ones(len(unclassified_points), dtype=bool)  # No NDVI filter applied

    # Filter points after applying NDVI
    ndvi_filtered_points = unclassified_points[ndvi_filter]

    # Step 4: 2D Clustering using DBSCAN (only x and y coordinates)
    coords_2d = np.vstack((ndvi_filtered_points.x, ndvi_filtered_points.y)).T
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords_2d)

    # Step 5: Filter Clusters by Area Threshold
    labels = clustering.labels_
    unique_labels, counts = np.unique(labels, return_counts=True)

    # Calculate minimum cluster size based on the minimum cluster area and point density
    min_cluster_size = int(min_cluster_area * point_density)

    # Keep only clusters that meet the minimum size threshold
    large_cluster_labels = unique_labels[counts >= min_cluster_size]
    vegetation_points = ndvi_filtered_points[np.isin(labels, large_cluster_labels)]

    # Write the filtered points to a new LAZ file
    with laspy.open(output_path, mode='w', header=las.header) as writer:
        writer.write_points(vegetation_points)

    print(f"Filtered vegetation points saved to {output_path}")

filter_tree_canopy(
    input_path='input.laz',
    output_path='vegetation_filtered.laz',
    bbx=(155000, 155500, 463000, 463500),  # Bounding box as (min_x, max_x, min_y, max_y)
    min_height=2.0,
    min_cluster_area=5,
    ndvi_threshold=0.2,
    eps=1.5,
    min_samples=5,
    point_density=1.5
)
