
import streamlit as st
from streamlit_option_menu import option_menu
import os

from utils import ModelRegistry, DeployModel, DatasetVersioning
from io import StringIO
import zipfile

# Using "with" notation
with st.sidebar:
    menu = option_menu(
        "Semi Automatic Labelling",
        ["Model Registry",
         "Model Deployment",
         "Dataset Upload",
         "Dataset Preprocessing",
         "Dataset Versioning"])

if menu == "Model Registry":
    st.title('Model Registry')
    st.write('Model Registry merupakan fungsi untuk mengunggah model ke Github Release Assets. \
        Assets tersebut selanjutnya diunduh sebagai model pada fungsi Model Deployment.')

    st.subheader('Repository')
    col01, col02, col03 = st.columns([3, 1, 1])
    with col01:
        repo_url = st.text_input(
            'Repository (*):', 'https://github.com/ruhyadi/model-registry')
    with col02:
        token = st.text_input(
            'Token (*):', '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')
    with col03:
        branch = st.text_input('Branch (*):', 'main')

    st.subheader('Releases')
    col11, col12, col13 = st.columns([2, 2, 1])
    with col11:
        release_title = st.text_input('Release title (*)', 'v1.0 release')
    with col12:
        release_desc = st.text_input(
            'Release description (*)', 'Release assets v1.0')
    with col13:
        release_tag = st.text_input('Release Tag (*)', 'v1.0')

    assets = st.file_uploader('Model Asset(s) (*)', accept_multiple_files=True)

    if assets:

        registry = ModelRegistry(git_url=repo_url, token=token)

        registry.clone_repo()
        st.success(f'Success Clone Repository {repo_url.split("/")[3:5]}')

        upload_url = registry.create_release(
            release_title, release_tag, branch, release_desc)
        st.success(f'Success Release {release_tag}')

        for asset in assets:
            # save file
            filename = asset.name
            with open(os.path.join(os.getcwd(), filename), 'wb') as f:
                f.write((asset).getbuffer())

            registry.upload_assets(filename, upload_url)

if menu == 'Model Deployment':
    st.title('Model Deployment')
    st.write('Model Deployment merupakan fungsi untuk mendeploy model ke CVAT. \
        Fungsi ini akan cloning repository model (model registry) dan mendeploy model tersebut \
        pada CVAT lewat Nuclio.')

    st.subheader('Repository')
    cols01, cols02, cols03 = st.columns([2, 1, 1])
    with cols01:
        repo = st.text_input(
            "Repository", "https://github.com/ruhyadi/model-registry")
    with cols02:
        token = st.text_input('Token', "xxx")
    with cols03:
        branch = st.text_input("Tag Release", "v1.0")

    deploy_btn = st.button('Deploy Model')
    if deploy_btn:
        # init model deployment
        Deployment = DeployModel(
            url=repo,
            remote='/home/intern-didir/Repository/labelling/apps/cvat',
            branch=branch,
            token=token,
            gpu=False,
        )
        Deployment.clone_repo()
        Deployment.deploy_model()

if menu == "Dataset Upload":
    st.title("Dataset Upload")
    st.write('Fungsi digunakan untuk meng-upload dataset baru.')

    st.subheader('Repository')

    col01, col02, col03 = st.columns([3, 1, 1])
    with col01:
        repo_url = st.text_input(
            'Repository (*):', placeholder='https://github.com/ruhyadi/sample-release')
    with col02:
        token = st.text_input('Token (*):', placeholder="xxx")
    with col03:
        branch = st.text_input('Tag (*):', placeholder="vX.X")

    uploaded_file = st.file_uploader('Dataset (*):', type=".zip")
    upload_btn = st.button('Upload')

    if upload_btn:
        if repo_url is None:
            st.write("Repo empty")

        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()

            file = open('/tmp/test.zip', 'wb')
            file.write(bytes_data)
            file.close()


if menu == "Dataset Preprocessing":
    st.title("Dataset Preprocessing")
    st.write('Fungsi digunakan untuk melakukan preprocessing dataset.')

    st.subheader('Repository')

    col01, col02, col03 = st.columns([3, 1, 1])
    with col01:
        repo_url = st.text_input(
            'Repository (*):', placeholder='https://github.com/ruhyadi/sample-release')
    with col02:
        token = st.text_input('Token (*):', placeholder='xxx')
    with col03:
        branch = st.text_input('Tag (*):', placeholder='vX.X')

    st.multiselect("Select Preprocessing Operations", [
                   "Grayscale", "Resize", "Dedupe"])

    preprocess_btn = st.button("Preprocess")

    if preprocess_btn:
        c = st.container()
        preview_btn = c.button('Preview')
        cvat_btn = c.button('Send to CVAT')

if menu == "Dataset Versioning":
    st.title('Dataset Versioning')
    st.write('Dataset Versioning merupakan fungsi untuk melakukan versioning dataset. \
        Dataset tersebut berasal dari dataset CVAT yang sudah dianotasi. Dataset \
        selanjutnya akan diunggah ke Remote Storage.')

    st.subheader('Repository')
    col01, col02, col03, col04 = st.columns([1, 3, 1, 1])
    with col01:
        dataset_type = st.radio(
            'Dataset Type:', ('Projects', 'Tasks'), key='radio001')
    with col02:
        repo = st.text_input('Dataset Registry (Repository):',
                             'https://github.com/ruhyadi/dataset-registry')
    with col03:
        token = st.text_input('Token (*):', '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')
    with col04:
        version = st.text_input('Dataset Version:', 'v1.0')

    col11, col12, col13 = st.columns([2, 1, 2])
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

    st.subheader('Remote Storage')
    col21, col22, col23 = st.columns([1, 2, 1])
    with col21:
        remote = st.selectbox(
            'Remote Storage:', ('Google Drive', 'Azure Blob'))
    with col22:
        endpointurl = st.text_input('Endpoint URL:', '1quvC2xMB89od6V0HPDf-wCpttU4XTP9t')
    with col23:
        auth_token = st.text_input('Authorization Token:', 'xxx')

    upload_btn = st.button('Versioning Dataset')

    if upload_btn:
        dataset = DatasetVersioning(
            dataset_type=dataset_type,
            repo=repo,
            dataset_version=version,
            ids=ids,
            filename=filename,
            annot_type=annot_type,
        )

        # clone repository
        dataset.clone_repo()

        # download dataset from cvat
        dataset.download_dataset()

        # push to storage
        dataset.push_to_remote(endpointurl=endpointurl)

        # versioning
        dataset.versioning_git()
