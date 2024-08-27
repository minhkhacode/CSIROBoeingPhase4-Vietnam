import geopandas as gpd
import numpy as np


def load_data_geo(path: str):
    gdf = gpd.read_file(path)
    return gdf


#########################################################
def eliminate_noise(qr, og_square):
    test_sq = np.squeeze(qr)
    square =0
    for x in range(test_sq.shape[0]):
        for y in range(test_sq.shape[1]):
            if(not np.isnan(test_sq[x][y])):
                square += 100

    if(square/og_square < 0.75):
         return qr.where(False, np.nan)
    return qr



#########################################################
def process(HT_MAP, polygon, label, CODE_MAP, ouput_image, squares):
    result = {}
    sub_result= {}
    for key, values in HT_MAP.items():
        print(f"process {key}")
        array_list = []
        deleted_array = []
        for i in range(len(polygon)):
            po = polygon[i]
            lb = label[i]
            code_lb = CODE_MAP.get(lb, 15)
            s = 0
            try:
                qr = ouput_image.rio.clip([po], "EPSG:9209")
                if code_lb in values["data"]:
                    if code_lb == 6:
                        qr = qr.where((qr != 6.0), np.nan)
                        # qr = qr.where((qr != 3.0), np.nan)
                    elif code_lb == 15:
                        qr = qr.where((qr != 6.0), np.nan)
                        qr = qr.where((qr != 3.0), np.nan)
                    else: 
                        qr = qr.where(qr != float(code_lb), np.nan)


                    # print(qr)
                else:
                    qr.values[:, :, :] = np.nan
                #calculate square and eliminte small pieces 
                new_qr = eliminate_noise(qr, squares[i])
                # print(squares[i])
                array_list.append(qr)
                deleted_array.append(new_qr)
            except Exception as e:
               print(e)
        result.update({key: array_list})
        sub_result.update({key: deleted_array})
    return result, sub_result