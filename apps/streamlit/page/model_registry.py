"""
Page for model serving
"""

import streamlit as st
import os
from function.repository import Repository

def model_registry(page_key: str = 'model_registry'):
    """ page for model registry """
    st.header('Model Registry')

    st.subheader('Clone Repository')
    col0 = st.columns([3, 2, 1])
    with col0[0]: 
        url = st.text_input(
            label='Repository URL',
            value='https://github.com/username/reponame',
            key=page_key)
    with col0[1]:
        token = st.text_input(
            label='Personal Access Token',
            value='xxx',
            key=page_key,
            type='password')
    with col0[2]:
        branch = st.text_input(
            label='Branch',
            value='main',
            key=page_key)

    st.subheader('Release Assets')
    col1 = st.columns([2, 2, 1])
    with col1[0]:
        title = st.text_input(
            label='Release Title',
            value='Model v1.0',
            key=page_key)
    with col1[1]:
        desc = st.text_input(
            label='Release Description',
            value='Release v1.0 of xxx model',
            key=page_key)
    with col1[2]:
        tag = st.text_input(
            label='Release Tag',
            value='v1.0',
            key=page_key)

    assets = st.file_uploader(label='Model Asset(s)', accept_multiple_files=True, 
            key=page_key)

    release_btn = st.button(label='Release Assets', key=page_key)

    if release_btn:
        repo = Repository(repo_url=url, ref=branch, token=token)
        # clone repo
        repo.clone(force=True)
        st.success(f'Success Clone Repository {url.split("/")[3:5]}')

        # create release.txt
        # actually dummy file for purpose git able to commit
        with open(os.path.join(repo.repo_dir, 'release.txt'), 'w') as f:
            f.write(desc)
            
        try:
            # create release
            repo.create_release(title=title, desc=desc, tag=tag, branch=branch, with_commit=True)
            release_id = repo.get_release(tag=tag)
            st.success(f'Create release {tag} with id {release_id}')
        except:
            # if fail, get existing release id
            release_id = repo.get_release(tag=tag)
            st.success(f'Found release {tag} with id {release_id}')
        
        for asset in assets:
            filename = asset.name
            with open(os.path.join(repo.repo_dir, filename), 'wb') as f:
                f.write((asset).getbuffer())
                
            repo.upload_assets(filename=filename, release_id=release_id)
            st.success(f'Success Releasing Asset {filename}')