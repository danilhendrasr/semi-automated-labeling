""" Dataset Versioning """

import os
from git import Repo

import streamlit as st
from function import fiftyone51
from function.repository import Repository
from function.dvc import DVC
from function import cvat
from function.report import GenerateReport


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
            # TODO: fix reference tag
            repo = Repository(repo_url=url, ref=merge_ref, token=token, dump_dir=dump_dir)
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
        st.success(f'Success Clone Dataset Registry {"/".join(url.split("/")[3:5])}')

        # init DVC
        dvc = DVC(path=repo.repo_dir)

        # donwload dataset
        # TODO: apply merging with fiftyone
        if is_merging == "True":
            dataset.tasks_dump(
                task_id=task_id,
                fileformat=annot_type,
                filename="new_dataset.zip",
                extract=True,
                remove_zip=True,
                to_fiftyone=True
            )
        else:
            dataset.tasks_dump(
                task_id=task_id,
                fileformat=annot_type,
                extract=True,
                remove_zip=True,
                to_fiftyone=True
            )
        st.success(f"Download Dataset Task {task_id}")

        # pull dataset for merging
        if is_merging == "True":
            dvc.pull()
            # rename dataset directory from dvc pull
            os.rename(os.path.join(repo.repo_dir, "dataset"), os.path.join(repo.repo_dir, "old_dataset"))
            fiftyone51.merging_dataset(format=annot_type, repo_dir=repo.repo_dir)
            st.success(f'Success Merging {merge_ref} to {ref}')

        # add dataset to dvc
        repo.checkout(ref='main')
        dvc.add(item="dataset")
        st.success(f"Success Add Dataset to DVC")

        # # create report
        # report = GenerateReport(
        #     repo_dir=repo.repo_dir,
        #     format=annot_type,
        #     version=ref,
        #     desc=desc,
        #     filename="README"
        # )
        # report.generate()

        # versioning dataset
        repo.create_release(title=title, desc=desc, tag=ref, with_commit=True)
        st.success(f"Success Versioning Dataset on {ref}")

        # push dvc to remotes storage
        dvc.push()
        st.success(f"Success Push to Remotes Storage")
