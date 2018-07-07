import requests

def ElevQuery10M(lat,lon):
    params = '/epqs/pqs.php?x=%.6f&y=%.6f&units=FEET&output=json'% (lon, lat)
    usgs = requests.get('http://ned.usgs.gov'+ params)
    response = usgs.json()
    if usgs.status_code == 200:
        return response['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']
    else:
        return response 
    
