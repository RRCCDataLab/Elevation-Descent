import xml.etree.ElementTree as ET
import numpy as np

# Meta data XML files are stored with the raster data in the DEM_Database
def get_bounds_from_meta(path_to_meta_XML):
    with open(path_to_meta_XML, 'rt') as f:
        tree = ET.parse(f)

    root = tree.getroot()
    N_bound = float(root[0][4][0][2].text)
    S_bound = float(root[0][4][0][3].text)
    E_bound = float(root[0][4][0][1].text)
    W_bound = float(root[0][4][0][0].text)

    return N_bound, S_bound, E_bound, W_bound

def find_nearest(array, value):
    index = (np.abs(array - value)).argmin()
    return index
