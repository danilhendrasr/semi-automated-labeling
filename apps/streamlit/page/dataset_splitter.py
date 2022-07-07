"""Split dataset into gt and preds"""

import streamlit as st
import os

from function.fiftyone51 import Splitter
from function.cvat import CVAT
import json
from glob import glob


def dataset_splitter(page_key: str = "dataset_splitter", dump_dir: str = os.getcwd()):
    """Split dataset into gt and preds"""

    # state
    if "cvat" not in st.session_state:
        st.session_state.cvat = None
    if "splitter" not in st.session_state:
        st.session_state.splitter = None

    st.header("Dataset Splitter")
    st.write("Feature Dataset Splitter berfungsi untuk mem-split Task besar \
        menjadi Task yang lebih kecil. Salah satu fungsi kongkrit dari fitur ini dapat \
        digunakan untuk mem-split Task Prediction menjadi Task Ground-Truth.")

    st.subheader("Dataset Split Parameters")
    col1 = st.columns([2, 2, 3])
    with col1[0]:
        task_id = st.text_input(label="Task ID", value="52", key=f"{page_key}")
    with col1[1]:
        percentage = st.text_input(
            label="Percentage %", value="10", key=f"{page_key}")

    col_btn = st.columns([2, 2, 3])
    with col_btn[0]:
        split_btn = st.button(label="Split Dataset")
    with col_btn[1]:
        send_btn = st.button(label="Send to CVAT")

    if split_btn:
        is_cvat_configured = bool(st.session_state.cvat_host) and bool(
            st.session_state.cvat_username) and bool(st.session_state.cvat_password)

        if not is_cvat_configured:
            st.error(
                "CVAT hasn't configured, please configure it in the Control Panel page")
            return

        cvat_host = st.session_state.cvat_host
        cvat_username = st.session_state.cvat_username
        cvat_password = st.session_state.cvat_password

        # initalize CVAT
        st.session_state.cvat = CVAT(
            username=cvat_username,
            password=cvat_password,
            host=cvat_host,
            dump_dir=dump_dir,
        )
        # download dataset
        st.session_state.cvat.tasks_dump(
            task_id=task_id,
            fileformat="COCO 1.0",
            filename=f"{task_id}.zip",
            extract=True,
            remove_zip=True,
            to_fiftyone=True,
        )
        dataset_dir = os.path.join(dump_dir, task_id)
        # initialize splitter
        st.session_state.splitter = Splitter(
            task_id=task_id,
            percentage=percentage,
            dataset_dir=dataset_dir,
            dump_dir=dump_dir,
        )
        # get info
        preds, gt = st.session_state.splitter.get_info()
        col2 = st.columns([2, 2, 2])
        with col2[0]:
            st.metric(label=f"Total Task #{task_id} Images", value=preds)
        with col2[1]:
            st.metric(label="Total New Task Images", value=gt)

    if send_btn:
        # split dataset
        st.session_state.splitter.split()
        st.success(f"Success Split Dataset to {percentage}%")
        # get labels classes
        labels_json = json.load(
            open(os.path.join(dump_dir, f"{task_id}_gt", "labels.json"), "r"))
        classes = [data for data in labels_json['categories']
                   if data['id'] != 0]
        images = sorted(
            glob(os.path.join(dump_dir, f"{task_id}_gt", "data", "*")))

        created_id = st.session_state.cvat.tasks_create(
            name=f"Split_{percentage}%_From_#{task_id}",
            labels=classes,
            resource_type="local",
            resources=images
        )
        st.success(f"Success Upload Dataset to CVAT on Task {created_id}")
