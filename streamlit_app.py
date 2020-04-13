import os, json
import pandas as pd
import streamlit as st
import numpy as np

'''
## FitBit Data
This is real-world data for myself.\n
Select from the data values, and frequency. You may also change the time period by clicking the arrow in the top-left corner.
'''

@st.cache(suppress_st_warning=True, show_spinner=False)
def load_data(string, list_dir = '../DanielCorley/user-site-export', save=False):
    
    '''
    pass in the first three letters of the file you're trying to load:
        ['steps', 'distance', 'heart', 'sleep', 'est_oxygen']
    '''
    file_dict = {
        'steps': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUlmEk_WBNoO1rKq8SsFL5Owd1PndQ8DsXxA9CbaJsaK6HJkD7G1mCLID-_THzPT4DDnY787S64PSh/pub?gid=1166746621&single=true&output=csv',
        'distance': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUlmEk_WBNoO1rKq8SsFL5Owd1PndQ8DsXxA9CbaJsaK6HJkD7G1mCLID-_THzPT4DDnY787S64PSh/pub?gid=508142528&single=true&output=csv',
        'heart_rate': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUlmEk_WBNoO1rKq8SsFL5Owd1PndQ8DsXxA9CbaJsaK6HJkD7G1mCLID-_THzPT4DDnY787S64PSh/pub?gid=0&single=true&output=csv',
        'sleep': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUlmEk_WBNoO1rKq8SsFL5Owd1PndQ8DsXxA9CbaJsaK6HJkD7G1mCLID-_THzPT4DDnY787S64PSh/pub?gid=25587178&single=true&output=csv',
        'est_oxygen': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUlmEk_WBNoO1rKq8SsFL5Owd1PndQ8DsXxA9CbaJsaK6HJkD7G1mCLID-_THzPT4DDnY787S64PSh/pub?gid=2146445686&single=true&output=csv'
    }
    
    try:
        df = pd.read_csv(file_dict[string])
        if string == 'sleep':
            df.rename(columns={'minutesAsleep':'hoursAsleep'}, inplace=True)
            
        with st.spinner('processing datetime'):
            df['dateTime'] = pd.to_datetime(df['dateTime'])
            df.set_index('dateTime', inplace=True)
                
        return df
    
    # while deployed, this will come into play when allowing users to upload their own files
    except IOError:
        # show files that contain the data we are loading
        files = [x for x in os.listdir(list_dir) if x[:3] == string[:3]][:3000]
        num_files = len(files)
        txt = st.write(f'number of files: {num_files}')
        
        # deciding if we will be loading jsons or csvs
        file_type = None
        try:
            pd.read_json(f'{files[0]}')
            file_type = 'json'
            st.spinner('loading json')
        except:
            file_type = 'csv'
            st.spinner('loading csv')
            
        # iterate over the files and append to one dataframe
        df = pd.DataFrame()
        # instantiate loading bar
        my_bar = st.progress(0)
        num_list = [int(x) for x in np.linspace(0,100, num_files+1)]
        
        for i,file in enumerate(files):
            if file_type == 'json':
                df = df.append(pd.read_json(f'{list_dir}/{file}'))
            else:
                df = df.append(pd.read_csv(f'{list_dir}/{file}'))
                
            # add to the progress bar by num files already loaded
            my_bar.progress(num_list[i+1])
        # delete progress bar
        my_bar.empty()
        
        # to_datetime
        with st.spinner('processing datetime'):
            if string in ['steps', 'distance', 'heart']:
                df['dateTime'] = pd.to_datetime(df['dateTime'])
                df.set_index('dateTime', inplace=True)
            elif string in ['sleep']:
                df['startTime'] = pd.to_datetime(df['startTime'])
                df.set_index('startTime', inplace=True)
                df.rename(columns={'minutesAsleep':'hoursAsleep'}, inplace=True)
            else:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                df.rename(columns={'Infrared to Red Signal Ratio':'oxy'}, inplace=True)
        if save:
            df.to_pickle(file_dict[string])
        
        return df
        
        
value = st.selectbox('what data would you like to look at?', ['Select Data:','steps', 'distance', 'heart_rate', 'sleep', 'est_oxygen'])

if value != 'Select Data:':
    
    df = load_data(value).fillna(method='bfill')
    
    min_date = st.sidebar.date_input('min date', df.index.min())
    max_date = st.sidebar.date_input('max date', df.index.max())

    df_size = df.loc[f'{min_date}':f'{max_date}'].shape
    
    resamp = st.selectbox('how do you want to see the data?', ['daily','weekly'])
    df = df.loc[f'{min_date}':f'{max_date}']
    
    rolling = st.checkbox('rolling avg?')
    
    if value in ['heart_rate','sleep']:
        if resamp == 'weekly':
            df = df.resample('w').mean()
            average = df.iloc[:,0].mean()
        else:
            average = df.iloc[:,0].mean()
    else:
        if resamp == 'weekly':
            df = df.resample('w').sum()
            average = df.iloc[:,0].mean()
        else:
            average = df.iloc[:,0].mean()
    
    if rolling:
        if resamp == 'weekly':
            df['rolling_week'] = df.rolling(4).mean()
        else:
            df['rolling'] = df.rolling(30).mean()
    
    if value == 'sleep':
        'This may look like I don\'t sleep alot, but FitBit has a "sensitive" sleep setting, which is the lower. More on that [here](https://community.fitbit.com/t5/Sleep-Better/Inaccurate-Sleep-Log-Change-your-settings/td-p/1406238)'
    
    st.write(f'average {resamp} {value}: {int(average):,d}'.replace('_',' '))
    st.line_chart(df)
    
    if st.checkbox('show data'):
        st.write(df)