import os, json
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

'''
# FitBit Data
'''

@st.cache(suppress_st_warning=True, show_spinner=False)
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
        st.write('pickle')
        return df
    
    except IOError:
        files = [x for x in os.listdir(list_dir) if x[:3] == string[:3]][:3000]
        num_files = len(files)
        txt = st.write(f'number of files: {num_files}')
        
        file_type = None
        try:
            pd.read_json(f'{list_dir}/{files[0]}')
            file_type = 'json'
            st.spinner('loading json')
        except:
            file_type = 'csv'
            st.spinner('loading csv')
            
#         iterate over the files and append to one dataframe
        df = pd.DataFrame()
        my_bar = st.progress(0)
        
        num_list = [int(x) for x in np.linspace(0,100, num_files+1)]
        
        for i,file in enumerate(files):
            
            if file_type == 'json':
                df = df.append(pd.read_json(f'{list_dir}/{file}'))
            else:
                df = df.append(pd.read_csv(f'{list_dir}/{file}'))
            my_bar.progress(num_list[i+1])
            
        my_bar.empty()
        
        with st.spinner('processing datetime'):
            if string in ['steps', 'distance', 'heart']:
                df['dateTime'] = pd.to_datetime(df['dateTime'])
                df.set_index('dateTime', inplace=True)
            elif string in ['sleep']:
                df['startTime'] = pd.to_datetime(df['startTime'])
                df.set_index('startTime', inplace=True)
                
            else:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                df.rename(columns={'Infrared to Red Signal Ratio':'oxy'}, inplace=True)
        
        df.to_pickle(file_dict[string])
        
        
        return df
        
        
value = st.selectbox('what data would you like to look at?', ['Select Data:','steps', 'distance', 'heart', 'sleep', 'est_oxygen'])

if value != 'Select Data:':
    
    df = load_data(value)
    
    min_date = st.sidebar.date_input('min date', df.index.min())
    max_date = st.sidebar.date_input('max date', df.index.max())

    df_size = df.loc[f'{min_date}':f'{max_date}'].shape
    
    resamp = st.selectbox('How do you want to see the data', ['daily','weekly'])
    df = df.loc[f'{min_date}':f'{max_date}']
    
    if value == 'heart':
        df['bpm'] = df.value.map(lambda x: x['bpm'])
        df.drop(columns=['value'], inplace=True)
        if resamp == 'daily':
            df = df.resample('d').mean()   
        elif resamp == 'weekly':
            df = df.resample('w').mean()
    elif value == 'sleep':
            df = df['minutesAsleep']
            if resamp == 'daily':
                df = df.resample('d').mean()/60
            elif resamp == 'weekly':
                df = df.resample('w').mean()/60

    else:
        if resamp == 'daily':
            df = df.resample('d').sum()   
        elif resamp == 'weekly':
            df = df.resample('w').sum()
        
    f'dataframe size: {df.shape}' 
    
    st.line_chart(df)
    
if st.checkbox('show data'):
    st.write(df)