"""
Dataset versioning with DVC
Proof of Concept with Streamlit
Contributor: Didi Ruhyadi (@ruhyadi)
"""
import streamlit as st
from utils import DatasetVersioning

def main():
    st.title('Dataset Versioning with DVC')
    st.markdown('Versioning CVAT Dataset and Annotations')

    col01, col02, col03 = st.columns(3)

    with col01:
        dataset_type = st.radio('Dataset Type:', ('Projects', 'Tasks'), key='radio001')

    with col02:
        repo = st.text_input('Dataset Registry (Repository):', 'https://github.com/ruhyadi/dataset-registry')

    with col03:
        version = st.text_input('Dataset Version:', 'v1.0')

    # _, col_token, _ = st.columns(3)

    # with col_token:
    #     token = st.text_input('Token', 'xxxxxx')

    col11, col12, col13 = st.columns(3)

    with col11:
        filename = st.text_input('Filename:', 'sample.zip')
    
    with col12:
        if dataset_type == 'Projects':
            ids = st.text_input('Projects ID:', '1')
        else:
            ids = st.text_input('Tasks ID:', '3')

    with col13:
        annot_type = st.selectbox(
            'Annotations Type:', 
            ('COCO 1.0', 'CVAT 1.1', 'PASCAL VOC 1.1', 'TFRecord 1.0', 'YOLO 1.1'))

    download_btn = st.button('Download')

    if download_btn:
        dataset = DatasetVersioning(
            dataset_type=dataset_type,
            repo=repo,
            dataset_version=version,
            ids=ids,
            filename=filename,
            annot_type=annot_type,
        )

        # # clone repository
        # dataset.clone_repo()

        # # download dataset from cvat
        # dataset.download_dataset()

        # push to storage
        dataset.push_to_remote()

        # versioning
        dataset.versioning_git()
        
if __name__ == '__main__':
    main()
