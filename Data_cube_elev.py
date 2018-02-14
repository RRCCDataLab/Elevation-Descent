'''
This program creates a tensor of (latitude, longitude, elevation) using google's
elevation query API. QUERYING TOO LARGE OF AN AREA WILL RESULT IN CHARGES FROM
GOOGLE.
'''
import google_ping as gp
# creates the lat, lon, elevation tensor using google_ping.py
# and saves it to a .npy file.
gp.googleElevReq()
