import streamlit as st

def inputs(key):
    col = st.columns([1, 1])
    with col[0]: width = st.text_input('Width', key=f'process resize : inputs width {key}')
    with col[1]: height = st.text_input('Height', key=f'process resize : inputs height {key}')
    params = (width, height)
    return params

def process(path, params):
    print(path, params)