import streamlit as st
import os
from PIL import Image

def inputs(function_key):
    params = None
    return params

def process(folder, params):
    print(f'Running process grayscale on {folder} with params {params}.')
    for path in os.listdir(folder):
        image = Image.open(os.path.join(folder, path)).convert('L')
        image.save(os.path.join(folder, path))
    print(f'Sucessfully run process grayscale on {folder} with params {params}.')