import sqlalchemy
import pandas as pd
import numpy as np
import trace

username = str(input('TSDC username: '))
password = str(input('TSDC password: '))
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

def create_engine():

    '''
    This function creates the SQL engine (connection to the Postgre server)
    '''

    # Build engine connection string
    username = str(input('username: '))
    password = str(input('password: '))
    hostname = str(input('hostname: '))
    database = str(input('database: '))

    # Start the engine
    SQLengine = sqlalchemy.create_engine(\
        "postgresql://{usr}:{pwd}@{host}/{db}".format(usr=username,\
                                                        pwd=password,\
                                                        host=hostname,\
                                                        db=database))

    return SQLengine


def batch_query(SQLengine, schema_name, table_name, first_row, last_row):


    '''
    This function creates the query and returns the query results,
    with batch size according the the last two input parameters
    '''

    # Build the query (PostgreSQL language query)
    SELECT = "SELECT *"
    # Could also use constructs like:
    # "SELECT column_name, column_name, column_name"
    # or
    # "SELECT column_name AS another_name"
    FROM = "{schema}.{table}".format(schema=schema_name, table=table_name)
    # Batch encodes the first and last row requested by the query
    BATCH = "LIMIT {limit} OFFSET {offset}".format(limit=last_row - first_row,\
                                                    offset=first_row)

    # Stitch the query together
    query = SELECT + FROM + BATCH

    return pd.read_sql(query, SQLengine)


# Primary subprocess function
def write_tbl_with_grade(schema_name, table_name, sample_num, veh_num):
    df = get_veh_tbl_df(schema_name, table_name, sample_num, veh_num)
    # Append bi-linearly interpolated elevation and grade to the table
    df = append_elev_and_grade(df)
    # Write new table to the database
    to_sql(df, schema_name, table_name+'_bilinCK')

def query(query_str):
    return pd.read_sql(query_str, SQLengine)

def get_veh_tbl_df(schema_name, table_name, sample_num, veh_num):
    query = get_query_str(schema_name, table_name, sample_num, veh_num)
    return pd.read_sql(query, SQLengine)

def get_both_grade(schema_name, table_name, sample_num, veh_num):
    query = '''\
SELECT tt_grade AS tomtom, bilin_grade as bilinear
FROM %s.%s
WHERE sampno = %i AND vehno = %i AND grdsrc1 = TRUE\
        ''' % (schema_name, table_name, sample_num, veh_num)
    df = pd.read_sql(query, SQLengine)
    return list(df['tomtom']), list(df['bilinear'])

def get_query_str(schema_name, table_name, sample_num, veh_num):
    SELECT = 'SELECT *, ST_Y(geom) AS lat, ST_X(geom) AS lon'
    FROM = '\nFROM ' + str(schema_name) + '.' + str(table_name)
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
def to_sql(tbl_df, schema_name, table_name):
    tbl_df.to_sql(table_name, SQLengine, schema=schema_name, if_exists='append', index=False)

def get_unique_veh_nums_df(schema_name, table_name):
    query = 'SELECT DISTINCT sampno, vehno FROM ' + str(schema_name) + '.' + str(table_name)
    return pd.read_sql(query, SQLengine)
