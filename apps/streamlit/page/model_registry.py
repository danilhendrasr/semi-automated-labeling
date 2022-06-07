"""
Page for model serving
"""

import streamlit as st
import os

from section import repository
from function.repository import Repository

def model_registry(page_key: str = 'model_registry'):
    """ page for model registry """
    st.header('Model Registry')
    url, token, ref = repository.clone(section_key=page_key)
    title, desc, tag, assets, btn = repository.release(section_key=page_key)

    if btn:
        repo = Repository(repo_url=url, ref=ref, token=token)
        # clone repo
        repo.clone(force=True)
        st.success(f'Success Clone Repository {url.split("/")[3:5]}')

        try:
            # create release
            repo.create_release(title=title, desc=desc, tag=tag)
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