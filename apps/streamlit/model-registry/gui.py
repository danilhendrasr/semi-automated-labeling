
import os
import streamlit as st
import git
from utils import ModelRegistry

def main():

    st.title('Model Registry')

    st.subheader('Repository')
    col01, col02, col03 = st.columns([3, 1, 1])
    with col01:
        repo_url = st.text_input('Repository (*):', 'https://github.com/ruhyadi/sample-release')
    with col02:
        token = st.text_input('Token (*):', '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')
    with col03:
        branch = st.text_input('Branch (*):', 'main')
    
    st.subheader('Releases')
    col11, col12, col13 = st.columns([2, 2, 1])
    with col11:
        release_title = st.text_input('Release title: (*)', 'v1.0 release')
    with col12:
        release_desc = st.text_input('Release description: (*)', 'Release assets v1.0')
    with col13:
        release_tag = st.text_input('Release Tag (*):', 'v1.0')

    assets = st.file_uploader('Model Asset(s) (*):', accept_multiple_files=True)

    assets_btn = st.button('Upload Assets')

    if assets_btn:
        
        registry = ModelRegistry(git_url=repo_url, token=token)

        registry.clone_repo()
        st.success(f'Success Clone Repository {repo_url.split("/")[3:5]}')

        upload_url = registry.create_release(release_title, release_tag, branch, release_desc)
        st.success(f'Success Release {release_tag}')

        for asset in assets:
            # save file
            filename = asset.name
            with open(os.path.join(os.getcwd(), filename), 'wb') as f:
                f.write((asset).getbuffer())

            registry.upload_assets(filename, upload_url)

if __name__ == '__main__':
    main()