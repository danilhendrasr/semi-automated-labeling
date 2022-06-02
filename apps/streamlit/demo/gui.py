import zipfile
import os

import streamlit as st
from streamlit_option_menu import option_menu
from ghapi.all import GhApi
from dotenv import load_dotenv

from utils import ModelRegistry, DeployModel, DatasetVersioning

load_dotenv()

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
        repo_name = st.text_input(
            'Repository (*):', placeholder='https://github.com/username/repo')
    with col02:
        gh_token = st.text_input(
            'Token (*):', placeholder='ghp_xxx')
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

        registry = ModelRegistry(git_url=repo_name, token=gh_token)

        registry.clone_repo()
        st.success(f'Success Clone Repository {repo_name.split("/")[3:5]}')

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
            "Repository", placeholder="https://github.com/username/repo-name")
    with cols02:
        gh_token = st.text_input('Token', placeholder="ghp_xxx")
    with cols03:
        branch = st.text_input("Tag Release", "v1.0")

    deploy_btn = st.button('Deploy Model')
    if deploy_btn:
        # init model deployment
        Deployment = DeployModel(
            url=repo,
            remote='/home/intern-didir/Repository/labelling/apps/cvat',
            branch=branch,
            token=gh_token,
            gpu=False,
        )
        Deployment.clone_repo()
        Deployment.deploy_model()

if menu == "Dataset Upload":
    st.title("Dataset Upload")
    st.write('Fungsi digunakan untuk meng-upload dataset baru. \
        Fungsionalitas ini akan membuat repository Github/Gitlab baru, \
            jadi API Token diperlukan untuk operasi ini.')

    st.subheader('Repository')

    col01, col02, col03, col04 = st.columns([3, 1, 1, 1])
    with col01:
        repo_name = st.text_input(
            'Repository Name (*):', placeholder='sample-release')
    with col02:
        repo_visibility = st.selectbox(
            "Repo visibility: ", ("Private", "Public"))
    with col03:
        gh_token = st.text_input(
            'Token (*):', placeholder="xxx")
    with col04:
        initial_tag = st.text_input('Tag (*):', "v1.0")

    uploaded_file = st.file_uploader('Dataset (*):', type=".zip")
    upload_btn = st.button('Upload')

    if upload_btn:
        if repo_name is None:
            st.write("Repo empty")

        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            NEW_REPO_DIR = "/tmp/dataset-upload"
            DATA_DIR = f"{NEW_REPO_DIR}/dataset"

            azure_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
            azure_access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")

            print(azure_account_name)
            print(azure_access_key)

            os.system(
                f"mkdir -p {NEW_REPO_DIR} \
                    && cd {NEW_REPO_DIR} \
                    && git init \
                    && git branch -M main \
                    && dvc init \
                    && dvc remote add -d main azure://dataset-upload \
                    && dvc remote modify --local main account_name '{azure_account_name}' \
                    && dvc remote modify --local main account_key '{azure_access_key}' \
                    && git add .dvc .dvcignore \
                    && git commit -m \"init dvc\"")

            os.mkdir(DATA_DIR)
            file = open(f'{DATA_DIR}/data.zip', 'wb')
            file.write(bytes_data)
            file.close()

            with zipfile.ZipFile(f'{DATA_DIR}/data.zip') as zipObj:
                zipObj.extractall(path=DATA_DIR)
                os.remove(f"{DATA_DIR}/data.zip")

                github_client = GhApi(token=gh_token)
                github_client.repos.create_for_authenticated_user(
                    name=repo_name, private=bool(repo_visibility == "Private"))

                os.system(f"cd {NEW_REPO_DIR} \
                    && dvc add dataset \
                    && git add .gitignore dataset.dvc \
                    && git commit -m \"add initial version of dataset\" \
                    && dvc push \
                    && git tag {initial_tag} \
                    && git remote add origin git@github.com:danilhendrasr/{repo_name} \
                    && git push -u origin main --tags")


if menu == "Dataset Preprocessing":
    st.title("Dataset Preprocessing")
    st.write('Fungsi digunakan untuk melakukan preprocessing dataset.')

    st.subheader('Repository')

    col01, col02, col03 = st.columns([3, 1, 1])
    with col01:
        repo_name = st.text_input(
            'Repository (*):', placeholder='https://github.com/username/repo-name')
    with col02:
        gh_token = st.text_input('Token (*):', placeholder='ghp_xxx')
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
                             placeholder='https://github.com/username/repo-name')
    with col03:
        gh_token = st.text_input(
            'Token (*):', placeholder='ghp_xxx')
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
        endpointurl = st.text_input(
            'Endpoint URL:', placeholder='1quvC2xMB89od6V0HPDf-wCpttU4XTP9t')
    with col23:
        auth_token = st.text_input('Authorization Token:', placeholder='xxx')

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
