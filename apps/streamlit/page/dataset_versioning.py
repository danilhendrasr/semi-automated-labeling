""" Dataset Versioning """

import os

import streamlit as st
from function.repository import Repository
import function.dvc_functions as depece
from function import cvat

def dataset_versioning(
    page_key: str = "dataset_versioning", dump_dir: str = os.getcwd()
):
    """Dataset versioning page"""
    st.header("Dataset Versioning")

    # Donwload Dataset
    st.subheader("Export Task Dataset")
    col0 = st.columns([2, 2])
    with col0[0]:
        username = st.text_input(
            label="Username", value="superadmin", key=f"{page_key}_versioning"
        )
    with col0[1]:
        password = st.text_input(
            label="Password",
            value="KECILSEMUA",
            key=f"{page_key}_versioning",
            type="password",
        )

    # repository clone section
    st.subheader("Dataset Registry")
    col0 = st.columns([3, 2, 1])
    with col0[0]:
        url = st.text_input(
            label="Repository URL",
            value="https://github.com/username/reponame",
            key=f"{page_key}_versioning",
        )
    with col0[1]:
        token = st.text_input(
            label="Personal Access Token",
            value="xxx",
            key=f"{page_key}_versioning",
            type="password",
        )
    with col0[2]:
        ref = st.text_input(label="Version", value="v1.0", key=f"{page_key}_versioning")

    col1 = st.columns([1, 2, 1, 1])
    with col1[0]:
        task_id = st.text_input(
            label="Task_id", value="39", key=f"{page_key}_versioning"
        )
    with col1[1]:
        annot_type = st.selectbox(
            label="Annotation Type",
            options=["YOLO 1.1", "COCO 1.0"],
            key=f"{page_key}_versioning",
        )
    with col1[2]:
        is_merging = st.radio(
            label="Merging Data?",
            options=["False", "True"],
            key=f"{page_key}_versioning",
        )
    # get dataset release version
    try:
        release_tags = Repository(repo_url=url, ref="main", token=token).list_release(
            get_tags=True
        )
    except:
        release_tags = []

    if is_merging == "True":
        with col1[3]:
            merge_ref = st.selectbox(label="Merging Dataset", options=release_tags)

    col2 = st.columns([1, 2])
    with col2[0]:
        remote_type = st.selectbox(
            label="Remote Storage",
            options=["gdrive", "azure"],
            key=f"{page_key}_versioning",
        )
    with col2[1]:
        endpoint = st.text_input(
            label="Endpoint",
            value="xxx",
            type="password",
            key=f"{page_key}_versioning",
        )

    btn = st.button(label="Versioning Dataset", key=f"{page_key}_versioning")

    if btn:
        repo = Repository(repo_url=url, ref="main", token=token, dump_dir=dump_dir)
        dataset = cvat.CVAT(
            username=username,
            password=password,
            host="http://192.168.103.67:8080",
            dump_dir=repo.repo_dir,
        )
        # clone repo
        repo.clone(force=True)
        st.success(f'Success Dataset Repository {"/".join(url.split("/")[3:5])}')
        # dump dataset
        dataset.tasks_dump(
            task_id=task_id,
            fileformat=annot_type,
            filename=f"{task_id}.zip",
            extract=True,
        )
        st.success(f"[INFO] Download Dataset Task {task_id}")
        # init dvc
        depece.init(repo_dir=repo.repo_dir, force=True)
        st.success(f"Success Init DVC")
        # add dataset to dvc
        depece.add(repo_dir=repo.repo_dir)
        st.success(f"Success Add Dataset to DVC")
        # add remotes
        depece.remote(
            repo_dir=repo.repo_dir,
            endpoint=endpoint,
            remotes=remote_type,
        )
        st.success(f"Success Add Remotes Storage")
        # tag version dataset
        repo.tag(tag=ref)
        st.success(f"Success Versioning Dataset on {ref}")
        # push dvc to remotes storage
        depece.push()
        st.success(f"Success Push to Remotes Storage")
