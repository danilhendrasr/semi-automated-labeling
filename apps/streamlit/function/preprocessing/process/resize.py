import streamlit as st

def inputs(function_key):
    col = st.columns([1, 1])
    with col[0]: width = st.text_input('Width', key=f'{function_key} input width')
    with col[1]: height = st.text_input('Height', key=f'{function_key} input height')
    params = (width, height)
    return params

def process(path, params):
    print(path, params)