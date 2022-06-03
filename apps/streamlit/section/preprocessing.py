import function
import streamlit as st

def preprocessing(path, available_preprocessing_list, section_key):
    st.subheader('Preprocessing')
    preprocess_col = st.columns([1, 2, 2])
    with preprocess_col[0]: add_preprocess = st.button('Add Preprocess', key=f'{section_key} add preprocess button') 
    with preprocess_col[1]: remove_preprocess = st.button('Remove Preprocess', key=f'{section_key} remove preprocess button')

    if f'{section_key} num_preprocess' not in st.session_state:
        st.session_state[f'{section_key} num_preprocess'] = 1
    if add_preprocess: st.session_state[f'{section_key} num_preprocess'] += 1
    if remove_preprocess: st.session_state[f'{section_key} num_preprocess'] = max(1, st.session_state[f'{section_key} num_preprocess']-1)
    
    preprocess_list = []
    for i in range(st.session_state[f'{section_key} num_preprocess']):
        choice = st.selectbox(f'Select Preprocess', available_preprocessing_list, key=f'{section_key} select-preprocess {i}')
        params = function.preprocessing.inputs(choice, key=f'{section_key} select-preprocess {i}')
        preprocess_list.append({
            'name' : choice,
            'params' : params
        })     
    
    process = st.button('Process', key=f'{section_key} process button')
    if process: function.preprocessing.preprocess(path, preprocess_list)