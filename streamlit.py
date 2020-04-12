import os, json
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

'''
 Hello World!
'''

@st.cache(suppress_st_warning=True)
def load_data(string, list_dir = '../DanielCorley/user-site-export'):
    
    '''
    pass in the first three letters of the file you're trying to load:
        ['ste', 'dis', 'hea', 'ste', 'est']
    '''
    file_dict = {
        'ste': 'step_df',
        'dis': 'dist_df',
        'hea': 'heart_df',
        'sle': 'sleep_df',
        'est': 'oxy_df'
    }
    if string not in file_dict:
        raise Exception('string not recognized!')
    
    try:
        df = pd.read_pickle(file_dict[string])
        print('loading from pickle')
        return df
    except IOError:
        print('loading from file storage')
        files = [x for x in os.listdir(list_dir) if x[:3] == string]
        st.write(f'example file name: {files[0]}')
        num_files = len(files)
        st.write(f'number of files: {num_files}')
        
        file_type = None
        try:
            pd.read_json(f'{list_dir}/{files[0]}')
            file_type = 'json'
            print('loading json')
        except:
            file_type = 'csv'
            print('loading csv')
            
        # iterate over the files and append to one dataframe
        df = pd.DataFrame()
        my_bar = st.progress(0)
        
        for i,file in enumerate(files):
            my_bar.progress(i + 1)
#             print(i, end=', ' if file != files[-1] else '\n')
            if file_type == 'json':
                df = df.append(pd.read_json(f'{list_dir}/{file}'))
            else:
                df = df.append(pd.read_csv(f'{list_dir}/{file}'))
#         df.to_pickle(file_dict[string])
        return df
    finally:
        print('files done!')
        

step_df = load_data('ste')

'steps', step_df