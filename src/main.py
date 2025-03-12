from pre_processing_new import preprocessing
from processing import process_buildings

def main():
    '''
    input path from s3
    '''
    # vector_path = r"C:\Users\zhuoyue.wang\Documents\Amsterdam_data\Height_validation\___Amsterdam\UTGLOBUS_Amsterdam.gpkg"
    # raster_path = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\Height_validation\ams_aoi1_building_dsm.tif'
    # aoi_path = r'https://wri-cities-heat.s3.us-east-1.amazonaws.com/NLD-Amsterdam/aoi1_data/AOI_l.gpkg'
    #
    # output_csv_path = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\Height_validation\AMS_ut_height_buildingdsm.csv'
    # output_vector_path = r'C:\Users\zhuoyue.wang\Documents\Amsterdam_data\Height_validation\AMS_ut_height_buildingdsm.GPKG'

    #vector_path = r"C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey\mty_overture_height1.geojson"
    vector_path = r'C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey\Monterrey_2\Monterrey_2.gpkg'
    raster_path = r'C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey/Mon_buildingdsm.tif'
    aoi_path = r'C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey/MTY_PRIORAREA.geojson'

    # output_csv_path = r"C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey\mty_overture_height.csv"
    # output_vector_path = r"C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey\mty_overture_height_upd.GPKG"
    output_csv_path = r"C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey\test\mty_ut_test.csv"
    output_vector_path = r"C:\Users\zhuoyue.wang\Documents\Building_height_Monterrey\test\mty_test.GPKG"

    # preprocessing
    cropped_raster, transform, nodata_value, cropped_vector = preprocessing(aoi_path, raster_path, vector_path)

    # Process each building in the cropped vector data
    building_stats, avg_diff, stddev_diff, updated_vector = process_buildings(cropped_raster, cropped_vector, transform, nodata_value, output_csv_path, output_vector_path)

    # # Display the results
    # print("Building Statistics:")
    # for building_id, stats in building_stats.items():
    #     print(f"Building ID {building_id}: {stats}")
    #
    # print(f"\nOverall Performance:")
    print(f"Average Difference: {avg_diff}")
    print(f"Standard Deviation of Difference: {stddev_diff}")

    
if __name__ == "__main__":
    main()