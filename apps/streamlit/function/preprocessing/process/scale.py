import streamlit as st

def inputs(function_key):
    scale = st.text_input('Scale', key=f'{function_key} input scale')
    params = scale
    return params

def process(path, params):
    print(path, params)