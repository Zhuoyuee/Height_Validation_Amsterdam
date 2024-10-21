# r'C:\Users\www\PycharmProjects\Height_Ams\data\Eubucco_vector_updated.gpkg'
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.patches as mpatches  # Import mpatches for creating legend
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Load your geopackage with the height difference data
gdf = gpd.read_file(r'C:\Users\www\PycharmProjects\Height_Ams\data\Eubucco_vector_updated.gpkg')

# Ensure everything is in EPSG:28992
gdf = gdf.to_crs(epsg=28992)

# Set up the plot
fig, ax = plt.subplots(figsize=(12, 12))

# Define bins based on mean and standard deviation
mean = 0.3656
std_dev = 2.4840
bins = [mean - 2 * std_dev, mean - std_dev, mean, mean + std_dev, mean + 2 * std_dev]

# Clip the height_difference column to this range and categorize
gdf['height_difference_clipped'] = gdf['height_difference'].clip(bins[0], bins[-1])
gdf['height_diff_class'] = np.digitize(gdf['height_difference_clipped'], bins)

# Create a color ramp avoiding yellow
colors = ['#2c7bb6', '#abd9e9', '#fdae61', '#d73027']
cmap = LinearSegmentedColormap.from_list('custom_cmap', colors)

# Plot the height difference data with the new color map
gdf.plot(column='height_diff_class', ax=ax, cmap=cmap, legend=True, legend_kwds={'label': "Height Difference (m)", 'shrink': 0.7})

# Add OSM basemap, using OpenStreetMap.Mapnik for sharp details
cx.add_basemap(ax, crs="EPSG:28992", source=cx.providers.OpenStreetMap.Mapnik, zoom=13)

# Set title
plt.title('Building Height Difference - Validation in Amsterdam', fontsize=15)

# Add scale bar
scalebar = ScaleBar(1, location='lower right', length_fraction=0.2)
ax.add_artist(scalebar)

# Add north arrow
ax.annotate('N', xy=(0.98, 0.95), xycoords='axes fraction', fontsize=15, ha='center', va='center',
            rotation=0, arrowprops=dict(facecolor='black', shrink=0.05))

# Adjust legend size and position
legend_labels = ['< {:.1f} m'.format(bins[0]), '{:.1f} to {:.1f} m'.format(bins[0], bins[1]),
                 '{:.1f} to {:.1f} m'.format(bins[1], bins[2]), '{:.1f} to {:.1f} m'.format(bins[2], bins[3]),
                 '> {:.1f} m'.format(bins[3])]
patches = [mpatches.Patch(color=cmap(i / (len(legend_labels) - 1)), label=label) for i, label in enumerate(legend_labels)]
ax.legend(handles=patches, loc='upper right', title='Height Difference (m)', fontsize=10)

# Show the plot
plt.tight_layout()
plt.show()
