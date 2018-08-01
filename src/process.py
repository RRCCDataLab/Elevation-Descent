import multiprocessing as mp
import sub_process as sp


schema_name = str(input('schema_name: '))
table_name = str(input('table_name: '))

def get_veh_inputs_lst(schema_name, table_name):
    # Get unique sampno and vehno
    unique_vehs_df = sp.get_unique_veh_nums_df(schema_name, table_name)

    # Build inputs as list of tuples
    schema_lst = [schema_name] * unique_vehs_df.shape[0]
    table_lst = [table_name] * unique_vehs_df.shape[0]
    sampno_lst = list(unique_vehs_df['sampno'])
    vehno_lst = list(unique_vehs_df['vehno'])
    
    # Return a list of tuples containing all sub_process params
    return zip(schema_lst, table_lst, sampno_lst, vehno_lst)

# Performs same function as sub_process.write_tbl_with_grade()
# but converts the arguments to tuple form to satisfy multiprocessing
def write_table_with_grade(veh_inputs_tuple):
    schema = veh_inputs_tuple[0]
    table = veh_inputs_tuple[1]
    sampno = veh_inputs_tuple[2]
    vehno = veh_inputs_tuple[3]
    sp.write_tbl_with_grade(schema, table, sampno, vehno)

# Run process
def append_grade_all_veh(max_cores):
    # Get veh_inputs list of tuples
    veh_inputs_lst = get_veh_inputs_lst(schema_name, table_name)

    # Initialize multiprocessing
    pool = mp.Pool(processes=max_cores)
    # Pass tuple arg sub process function and list of tuple args
    # Appends bilinearly interpolated elev and grade columns to entire table
    pool.map(write_table_with_grade, veh_inputs_lst)
    pool.terminate()
