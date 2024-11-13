import geopandas as gpd
from shapely.geometry import box
from pyproj import Transformer

# Load the GeoPackage (replace 'input.gpkg' with the actual file path)
input_gpkg = r'C:\Users\www\PycharmProjects\Height_Ams\data\3dglobpf_vector_updated.gpkg'
output_gpkg = r'C:\Users\www\WRI-cif\Validation_height\4326transform\3dglobpf_4326.gpkg'

# Load the geopackage with the original CRS (EPSG:28992)
gdf = gpd.read_file(input_gpkg)

# Reproject to EPSG:4326
gdf_4326 = gdf.to_crs(epsg=4326)

# Save the transformed geopackage
gdf_4326.to_file(output_gpkg, layer='transformed_layer', driver='GPKG')

# Create bounding box in EPSG:4326
xmin_28992, ymin_28992, xmax_28992, ymax_28992 = 120764.46, 483845.95, 122764.46, 485845.95

# Convert bounding box coordinates from EPSG:28992 to EPSG:4326
transformer_to_4326 = Transformer.from_crs("EPSG:28992", "EPSG:32631", always_xy=True)

xmin_4326, ymin_4326 = transformer_to_4326.transform(xmin_28992, ymin_28992)
xmax_4326, ymax_4326 = transformer_to_4326.transform(xmax_28992, ymax_28992)

# Return bounding box in EPSG:4326
bounding_box_4326 = {
    "xmin": xmin_4326,
    "ymin": ymin_4326,
    "xmax": xmax_4326,
    "ymax": ymax_4326
}

print(bounding_box_4326)
