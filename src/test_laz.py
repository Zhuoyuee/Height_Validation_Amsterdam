import laspy

def print_scalar_fields(input_path):
    las = laspy.read(input_path)
    # print("Available scalar fields in the LAZ file:")
    # #print(las.point_format.dimension_names)  # Prints all fields in the point format
    # print(list(las.point_format.dimension_names))

    min_reflectance = las['Reflectance'].min()
    max_reflectance = las['Reflectance'].max()
    print(f"Reflectance range: min={min_reflectance}, max={max_reflectance}")

# Run the function
print_scalar_fields(r'C:\Users\www\WRI-cif\Amsterdam\C_25GN1.LAZ')