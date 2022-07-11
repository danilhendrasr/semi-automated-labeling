import streamlit as st
import os
from PIL import Image

def inputs(function_key):
    col = st.columns([1, 1, 1])
    with col[0]: side = st.selectbox(f'Select Side', ['Width', 'Height'], key=f'{function_key} input select side')
    with col[1]: comperator = st.selectbox(f'Select Side', ['less than', 'less than or equal to', 'greater than', 'greater than or equal to', 'equal to', 'not equal to'], key=f'{function_key} input select comperator')
    with col[2]: length = st.text_input(f'{side}', key=f'{function_key} input length')
    params = (side, comperator, length)
    return params

def process(folder, params):
    print(f'Running process resize on {folder} with params {params}.')
    side, comperator, length = params
    length = int(length)
    for path in os.listdir(folder):
        image = Image.open(os.path.join(folder, path))
        width, height = image.size
        
        valid = False
        if side == 'Width':
            if comperator == 'less than':
                if width < length: valid = True
            if comperator == 'less than or equal to':
                if width <= length: valid = True
            if comperator == 'greater than':
                if width > length: valid = True
            if comperator == 'greater than or equal to':
                if width >= length: valid = True
            if comperator == 'equal to':
                if width == length: valid = True
            if comperator == 'not equal to':
                if width != length: valid = True
        if side == 'Height':
            if comperator == 'less than':
                if height < length: valid = True
            if comperator == 'less than or equal to':
                if height <= length: valid = True
            if comperator == 'greater than':
                if height > length: valid = True
            if comperator == 'greater than or equal to':
                if height >= length: valid = True
            if comperator == 'equal to':
                if height == length: valid = True
            if comperator == 'not equal to':
                if height != length: valid = True
        
        if not valid:
            os.remove(os.path.join(folder, path))

    print(f'Sucessfully run process resize on {folder} with params {params}.')