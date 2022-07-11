import streamlit as st
import os
from PIL import Image

def inputs(function_key):
    col = st.columns([1, 1])
    with col[0]: width = st.text_input('Width', key=f'{function_key} input width')
    with col[1]: height = st.text_input('Height', key=f'{function_key} input height')
    params = (width, height)
    return params

def process(folder, params):
    print(f'Running process resize on {folder} with params {params}.')
    width, height = params
    width = int(width)
    height = int(height)
    for path in os.listdir(folder):
        image = Image.open(os.path.join(folder, path)).resize((width, height))
        image.save(os.path.join(folder, path))
    print(f'Sucessfully run process resize on {folder} with params {params}.')