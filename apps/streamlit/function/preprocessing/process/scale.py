import streamlit as st
import os
from PIL import Image

def inputs(function_key):
    scale = st.text_input('Scale', key=f'{function_key} input scale')
    params = scale
    return params

def process(folder, params):
    print(f'Running process scale on {folder} with params {params}.')
    scale = params
    scale = float(params)
    for path in os.listdir(folder):
        image = Image.open(os.path.join(folder, path))
        width, height = image.size
        width = int(width * scale)
        height = int(height * scale)
        image = image.resize((width, height))
        image.save(os.path.join(folder, path))
    print(f'Sucessfully run process scale on {folder} with params {params}.')