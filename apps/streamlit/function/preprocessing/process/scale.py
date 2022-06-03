import streamlit as st

def inputs(key):
    scale = st.text_input('Scale', key=f'process scale : inputs scale {key}')
    params = scale
    return params

def process(path, params):
    print(path, params)