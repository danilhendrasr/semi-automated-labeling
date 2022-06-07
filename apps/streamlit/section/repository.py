""" Repository section """

import streamlit as st

def clone(section_key: str, is_btn: bool = False):
    st.subheader('Clone Repository')
    col = st.columns([3, 2, 1])
    with col[0]: 
        url = st.text_input(
            label='Repository URL',
            value='https://github.com/username/reponame',
            key=f'{section_key}_clone')
    with col[1]:
        token = st.text_input(
            label='Personal Access Token',
            value='xxx',
            key=f'{section_key}_clone',
            type='password')
    with col[2]:
        ref = st.text_input(
            label='Branch/Tag',
            value='main/v1.0',
            key=f'{section_key}_clone')
    if is_btn:
        btn = st.button(label='Clone Repository', key=f'{section_key}_clone')
        return [url, token, ref, btn]
    return [url, token, ref]

def release(section_key: str):
    st.subheader('Release Assets')
    col = st.columns([2, 2, 1])
    with col[0]:
        title = st.text_input(
            label='Release Title',
            value='Model v1.0',
            key=f'{section_key}_release')
    with col[1]:
        desc = st.text_input(
            label='Release Description',
            value='Release v1.0 of xxx model',
            key=f'{section_key}_release')
    with col[2]:
        tag = st.text_input(
            label='Release Tag',
            value='v1.0',
            key=f'{section_key}_release')

    assets = st.file_uploader(label='Model Asset(s)', accept_multiple_files=True, 
            key=f'{section_key}_release')

    btn = st.button(label='Release Assets', key=f'{section_key}_release')
    
    return [title, desc, tag, assets, btn]