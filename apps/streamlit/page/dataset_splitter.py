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
    st.subheader("Split Dataset")

    col0 = st.columns([2, 2])
    with col0[0]:
        username = st.text_input(
            label="Username", value="superadmin", key=f"{page_key}"
        )
    with col0[1]:
        password = st.text_input(
            label="Password", value="KECILSEMUA", key=f"{page_key}", type="password"
        )

    col1 = st.columns([2, 2, 3])
    with col1[0]:
        task_id = st.text_input(label="Task ID", value="52", key=f"{page_key}")
    with col1[1]:
        percentage = st.text_input(label="Percentage %", value="10", key=f"{page_key}")

    col_btn = st.columns([2, 2, 3])
    with col_btn[0]:
        split_btn = st.button(label="Split Dataset")
    with col_btn[1]:
        send_btn = st.button(label="Send to CVAT")

    if split_btn:
        # initalize CVAT
        st.session_state.cvat = CVAT(
            username=username,
            password=password,
            host="http://192.168.103.67:8080",
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
            st.metric(label="Total Preds Images", value=preds)
        with col2[1]:
            st.metric(label="Total GT Images", value=gt)

    if send_btn:
        # split dataset
        st.session_state.splitter.split()
        st.success("Success Split Dataset")
        # get labels classes
        labels_json = json.load(open(os.path.join(dump_dir, f"{task_id}_gt", "labels.json"), "r"))
        classes = [data for data in labels_json['categories'] if data['id'] != 0]
        images = sorted(glob(os.path.join(dump_dir, f"{task_id}_gt", "data", "*")))

        st.session_state.cvat.tasks_create(
            name=f"Split_{percentage}%_From_#{task_id}",
            labels=classes,
            resource_type="local",
            resources=images
        )
        st.success("Success Upload Dataset to CVAT")