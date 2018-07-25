import sqlalchemy
import pandas as pd
import numpy as np
import trace

username = input(str('TSDC username: '))
password = input(str('TSDC password: '))
hostname = 'tsdc-server'
database = 'master'

SQLengine = sqlalchemy.create_engine(\
    "postgresql://{usr}:{pwd}@{host}/{db}".format(usr=username,\
                                                    pwd=password,\
                                                    host=hostname,\
                                                    db=database))

test_query = """
SELECT sampno, vehno, gpsspeed, time_rel, ST_X(geom) AS lon, ST_Y(geom) AS lat
FROM tsdc_txdot_san_antonio.v_points_nrel
WHERE sampno = 301137 AND vehno = 1
"""

def get_veh_tbl_df(table_name, sample_num, veh_num, tomtomgrade=True):
    query = get_query_str(table_name, veh_num, tomtomgrade=tomtomgrade)
    return pd.read_sql(query, SQLengine)

def get_query_str(tbl_name, veh_num, tomtomgrade=True):
    SELECT = 'SELECT sampno, vehno, gpsspeed, time_rel, ST_Y(geom) AS lat, ST_X(geom) AS lon'
    if tomtomgrade == True:
        SELECT += '' # TODO insert column name for TomTom grade
    FROM = '\nFROM ' + str(tbl_name)
    WHERE = '\nWHERE sampno = ' + str(sample_num) + ' AND vehno = ' + str(veh_num)
    return SELECT + FROM + WHERE

def get_lats_from_tbl(tbl_df):
    return list(tbl_df['lat'])

def get_lons_from_tbl(tbl_df):
    return list(tbl_df['lon'])

def append_elev_and_grade(tbl_df):
    lats = get_lats_from_tbl(tbl_df)
    lons = get_lons_from_tbl(tbl_df)
    traces = trace.Trace(lats, lons)
    elev = traces.elev
    grade = traces.grade
    # Add a NaN to the end of grade list to match length w/ elev
    grade.append(np.nan)
    tbl_df['bilin_elev'] = pd.Series(elev, index=tbl_df.index)
    tbl_df['bilin_grade'] = pd.Series(grade, index=tbl_df.index)
    return tbl_df

# NOTE: chunksize kwarg for df.to_sql sets batch-size for writing rows to db
def to_sql(tbl_df, tbl_name):
    tbl_df.to_sql(tbl_name, SQLengine, if_exists='append', index=False)
