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
    st.subheader("CVAT Dataset")
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
    col0 = st.columns([3, 2])
    with col0[0]:
        url = st.text_input(
            label="Repository URL",
            # value="https://github.com/username/reponame",
            value="https://github.com/ruhyadi/sample-dataset-registry",
            key=f"{page_key}_versioning",
        )
    with col0[1]:
        token = st.text_input(
            label="Personal Access Token",
            # value="xxx",
            value="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",
            key=f"{page_key}_versioning",
            type="password",
        )

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

    # INFO: Remote Storage and Endpoint (DEPRICATED)
    # col2 = st.columns([1, 2])
    # with col2[0]:
    #     remote_type = st.selectbox(
    #         label="Remote Storage",
    #         options=["gdrive", "azure"],
    #         key=f"{page_key}_versioning",
    #     )
    # with col2[1]:
    #     endpoint = st.text_input(
    #         label="Endpoint",
    #         value="xxx",
    #         type="password",
    #         key=f"{page_key}_versioning",
    #     )

    col3 = st.columns([2, 2, 1])
    with col3[0]:
        title = st.text_input(
            label=f"Release Title",
            value="Release Dataset vX.X",
            key=f"{page_key}_versioning",
        )
    with col3[1]:
        desc = st.text_input(
            label="Release Description",
            value="Release vX.X of Dataset XXX",
            key=f"{page_key}_versioning",
        )
    with col3[2]:
        ref = st.text_input(
            label="Release Version", value="v1.0", key=f"{page_key}_versioning"
        )

    btn = st.button(label="Versioning Dataset", key=f"{page_key}_versioning")

    if btn:
        # init repository
        if is_merging == "True":
            repo = Repository(
                repo_url=url, ref=merge_ref, token=token, dump_dir=dump_dir
            )
        else:
            # default to main branch
            repo = Repository(repo_url=url, ref="main", token=token, dump_dir=dump_dir)

        # init dataset
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
            task_id=task_id, fileformat=annot_type, extract=True, remove_zip=True
        )
        st.success(f"[INFO] Download Dataset Task {task_id}")

        # pull dataset for merging
        if is_merging == "True":
            depece.pull(repo_dir=repo.repo_dir)

        # CAUTION: dvc init (DEPRICATED)
        depece.init(repo_dir=repo.repo_dir, force=True)
        st.success(f"Success Init DVC")

        # add dataset to dvc
        depece.add(repo_dir=repo.repo_dir)
        st.success(f"Success Add Dataset to DVC")

        # # CAUTION: add remotes (DEPRICATED)
        # depece.remote(
        #     repo_dir=repo.repo_dir,
        #     endpoint="1PSuz_MQr61Zh1R2PzfnVjEecRWGkrvpV",
        #     remotes='gdrive',
        # )
        # st.success(f"Success Add Remotes Storage")

        # # tag version dataset
        repo.create_release(title=title, desc=desc, tag=ref, with_commit=True)
        # repo.tag(tag=ref)
        st.success(f"Success Versioning Dataset on {ref}")

        # push dvc to remotes storage
        depece.push(repo_dir=repo.repo_dir)
        st.success(f"Success Push to Remotes Storage")
