"""Dataset Qualitry"""

import streamlit as st
import os

from function.validac import Validac
from function.cvat import CVAT


def dataset_quality(page_key: str = "dataset_quality", dump_dir: str = os.getcwd()):
    """Dataset Quality"""

    # state
    if "cvat" not in st.session_state:
        st.session_state.cvat = None
    if "validac" not in st.session_state:
        st.session_state.validac = None

    st.header("Dataset Quality")

    st.subheader("Validac")
    col0 = st.columns([2, 2])
    with col0[0]:
        username = st.text_input(
            label="Username", value="superadmin", key=f"{page_key}"
        )
    with col0[1]:
        password = st.text_input(
            label="Password", value="KECILSEMUA", key=f"{page_key}", type="password"
        )

    col1 = st.columns([2, 2, 2])
    with col1[0]:
        gt_id = st.text_input(
            label="Task GT",
            value="1",
            key=f"{page_key}",
        )
    with col1[1]:
        pred_id = st.text_input(
            label="Task Prediction",
            value="2",
            key=f"{page_key}",
        )
    with col1[2]:
        iou = st.text_input(
            label="IOU",
            value="0.5",
            key=f"{page_key}",
        )

    col2 = st.columns([1, 1, 4])
    with col2[0]:
        validac = st.button(label="Validac")
    with col2[1]:
        preview = st.button(label="Preview")

    if validac:
        """validation annotations with ground truth"""
        st.session_state.cvat = CVAT(
            username=username,
            password=password,
            host="http://192.168.103.67:8080",
            dump_dir=dump_dir,
        )
        for task_id in [gt_id, pred_id]:
            st.session_state.cvat.tasks_dump(
                task_id=task_id,
                fileformat="COCO 1.0",
                filename=f"{task_id}.zip",
                extract=True,
                remove_zip=True,
                to_fiftyone=True,
            )

        # validate annotations
        st.session_state.validac = Validac(
            gt_id=gt_id, pred_id=pred_id, iou_threshold=iou, dump_dir=dump_dir
        )
        mAP = st.session_state.validac.compute_mAP()
        st.metric(label="mAP", value=round(mAP, 4))

    if preview:
        """preview evaluation to fiftyone"""
        st.session_state.validac.preview_evaluation()
