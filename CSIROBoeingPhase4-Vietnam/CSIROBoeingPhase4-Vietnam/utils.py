import geopandas as gpd
import numpy as np
import os
from rioxarray.merge import merge_arrays
import matplotlib.pyplot as plt



def load_data_geo(path: str):
    gdf = gpd.read_file(path)
    return gdf


#########################################################
def eliminate_noise_with_min_square(qr, min_square):
    test_sq = np.squeeze(qr)
    square =0
    for x in range(test_sq.shape[0]):
        for y in range(test_sq.shape[1]):
            if(not np.isnan(test_sq[x][y])):
                square += 100

    if(square < min_square):
         return qr.where(False, np.nan)
    return qr


def eliminate_noise_with_min_percent(qr, og_square, min_percent):
    test_sq = np.squeeze(qr)
    square =0
    for x in range(test_sq.shape[0]):
        for y in range(test_sq.shape[1]):
            if(not np.isnan(test_sq[x][y])):
                square += 100

    if(square/og_square < min_percent):
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
                new_qr = eliminate_noise_with_min_percent(qr, squares[i], 0.5)
                # new_qr = eliminate_noise_with_min_square(qr, 10000)
                # print(squares[i])
                array_list.append(qr)
                deleted_array.append(new_qr)
            except Exception as e:
               print(e)
        result.update({key: array_list})
        sub_result.update({key: deleted_array})
    return result, sub_result

############### save image to folder
def save_file(save_path , result, cmap, labels, HT_MAP, extension_name="", show=True):
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    for k, v in result.items():
        rs = merge_arrays(v, nodata = np.nan)
        rs.rio.to_raster(f"{save_path}/{k}-{extension_name}.tif")
        if(show):
            img = rs.plot(cmap=cmap, add_colorbar=False)
            cbar = plt.colorbar(img)
            cbar.ax.set_yticklabels(labels)
            plt.title(f'{HT_MAP[k]["name"]}')
            plt.axis('off')
            plt.show()  

