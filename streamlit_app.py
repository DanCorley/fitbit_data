import os, json
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

'''
# FitBit Data
'''

@st.cache(suppress_st_warning=True, show_spinner=True)
def load_data(string, list_dir = '../DanielCorley/user-site-export'):
    
    '''
    pass in the first three letters of the file you're trying to load:
        ['steps', 'distance', 'heart', 'sleep', 'est_oxygen']
    '''
    file_dict = {
        'steps': 'step_df',
        'distance': 'dist_df',
        'heart': 'heart_df',
        'sleep': 'sleep_df',
        'est_oxygen': 'oxy_df'
    }
    if string not in file_dict:
        raise Exception('string not recognized!')
    
    try:
        df = pd.read_pickle(file_dict[string])
        st.spinner('loading from pickle')
        return df
    except IOError:
        st.spinner('loading from file storage')
        files = [x for x in os.listdir(list_dir) if x[:3] == string[:3]][:4]
        st.write(f'example file name: {files[0]}')
        num_files = len(files)
        st.write(f'number of files: {num_files}')
        
        file_type = None
        try:
            pd.read_json(f'{list_dir}/{files[0]}')
            file_type = 'json'
            st.spinner('loading json')
        except:
            file_type = 'csv'
            st.spinner('loading csv')
            
        # iterate over the files and append to one dataframe
        df = pd.DataFrame()
        my_bar = st.progress(0)
        
        num_list = [int(x) for x in np.linspace(0,100, num_files+1)]
        
        for i,file in enumerate(files):
            
            if file_type == 'json':
                df = df.append(pd.read_json(f'{list_dir}/{file}'))
            else:
                df = df.append(pd.read_csv(f'{list_dir}/{file}'))
#         df.to_pickle(file_dict[string
            my_bar.progress(num_list[i+1])
        st.write(string)
        if string in ['steps', 'distance', 'heart']:
            df['dateTime'] = pd.to_datetime(df.dateTime)
            df.set_index('dateTime', inplace=True)
        elif string in ['sleep']:
            df.startTime = pd.to_datetime(df.startTime)
            df.set_index('startTime', inplace=True)
        else:
            df.timestamp = pd.to_datetime(df.timestamp)
            df.set_index('timestamp', inplace=True)
        
        return df
        
        
value = st.selectbox('what data would you like to look at?', ['Select Data:','steps', 'distance', 'heart', 'sleep', 'est_oxygen'])

file = st.file_uploader('upload')

if file:
    df = pd.read_csv(file)
    df.Month = pd.to_datetime(df.Month)
    df.set_index('Month', inplace=True)
    mn = df['Thousands of Passengers'].max()
    mx = df['Thousands of Passengers'].min()
    
    
    usr_input = st.number_input('more than?',value = 0, min_value=0, max_value= 300, step=10)
    if usr_input:
        df[df['Thousands of Passengers'] > usr_input].shape
    
# if file:
#     file = pd.read_csv(file, index_col = 0)
#     file_shape = file.shape[0]
#     num = st.number_input(f'insert a number smaller than {file_shape}',1)
#     if num >= file_shape:
#         st.error('number must be smaller!')
#     else:
#         file[['artist', 'album', 'song_title', 'sentiment']].iloc[num]

# if value != 'Select Data:':

#     st.write(value)
    
#     df = load_data(value)
    
#     min_date = st.date_input('min date', df.index.min())
#     max_date = st.date_input('max date', df.index.max())

#     df.rename(columns={'Infrared to Red Signal Ratio':'a'}, inplace=True)

#     df_size = df.loc[f'{min_date}':f'{max_date}'].shape
    
#     f'dataframe size: {df.shape}' 
#     df