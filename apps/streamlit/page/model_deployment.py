"""
Page for model deployment
"""

import streamlit as st
import os
from function.dvc import DVC

from function.repository import Repository
from function import cvat
from function import utils

def model_deployment(page_key: str = 'model_deployment', serverless_dir: str = os.getcwd()):
    """model deployment page"""

    # state
    if bool(st.session_state.serverless_dir):
        serverless_dir = st.session_state.serverless_dir

    st.header('Model Deployment')
    st.subheader('Model Repository')
    col = st.columns([3, 2, 1])
    with col[0]: 
        url = st.text_input(
            label='Repository URL',
            value='https://github.com/username/reponame',
            key=f'{page_key}_clone')
    with col[1]:
        token = st.text_input(
            label='Personal Access Token',
            value='xxx',
            key=f'{page_key}_clone',
            type='password')

    try:
        tags = Repository(repo_url=url, ref='main', token=token).list_release(get_tags=True)
    except:
        tags = []

    with col[2]:
        ref = st.selectbox(
            label='Model Tag',
            options=tags
        )

    btn = st.button(label='Deploy Model', key=f'{page_key}_clone')

    if btn:
        repo = Repository(repo_url=url, ref=ref, token=token, dump_dir=serverless_dir)

        # clone repo
        repo.clone(force=True)
        st.success(f'Success Clone Repository {"/".join(url.split("/")[3:5])}')
        utils.change_model_tag(repo_dir=repo.repo_dir, repo_url=url, tag=ref)

        # pull model from cloud storage
        dvc = DVC(path=repo.repo_dir)
        dvc.pull()

        # deploy model
        cvat.deploy_model(repo_dir=repo.repo_dir, serverless_dir=serverless_dir)