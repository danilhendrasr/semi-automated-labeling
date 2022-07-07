""" Post Annotations Page """

import os
import numpy as np
import streamlit as st
from bokeh.models.widgets import Div

from function import fiftyone51
from function import cvat
from function import utils


def post_annotations(dump_dir: str, port: int = 6161):

    # state
    if "patches" not in st.session_state:
        st.session_state.patches = None
    if "tags" not in st.session_state:
        st.session_state.tags = None
    if "cvat_dataset" not in st.session_state:
        st.session_state.cvat_dataset = None
    if "dataset" not in st.session_state:
        st.session_state.dataset = None
    # assign unique tags
    try:
        unique_tags = np.unique(st.session_state.tags)
    except:
        unique_tags = []
    # get classes list
    try:
        classes = st.session_state.dataset.get_classes('ground_truth')
        # classes = [c for c in classes if c != "0"]
    except:
        classes = []

    st.header("Label Evaluator")
    st.write("Feature Label Evaluator berfungsi untuk mengevaluasi label bounding-box dataset. \
        Feature ini menggunakan FiftyOne sebagai explorer untuk mengevaluasi label bounding-box. \
        Label yang salah dapat ditandai dan diubah menjadi label yang benar.")

    st.subheader("CVAT Authentications")

    col1 = st.columns([2, 2, 2, 2])
    with col1[0]:
        task_id = st.text_input(label="Task Id", value="39")
    with col1[1]:
        iou_thres = st.text_input(label="NMS IoU Threshold", value="0.5")
    with col1[2]:
        with_embd = st.radio(label="With Embedding", options=["True", "False"])

    col2 = st.columns([2, 2, 4])
    with col2[0]:
        btn = st.button(label="Preview Labels")
    with col2[1]:
        save_tags_btn = st.button(label="Save Label Tags")

    st.subheader("Label Changer")
    st.write("Fungsi Label Changer berfungsi untuk mengubah label dari bounding-box yang sudah ditandai (tag).")

    col2 = st.columns([2, 2, 1, 1])
    with col2[0]:
        from_tag = st.selectbox(
            label="From Tag",
            options=unique_tags
        )
    with col2[1]:
        to_label = st.selectbox(
            label="To Label",
            options=classes
        )
    convert_btn = st.button(label="Convert Label")

    # st.subheader("Send Back to CVAT")
    # send_to_cvat_btn = st.button(label="Send Back to CVAT")

    # init dataset directory
    dataset_dir = os.path.join(dump_dir, task_id)

    if btn:
        is_cvat_configured = bool(st.session_state.cvat_host) and bool(
            st.session_state.cvat_username) and bool(st.session_state.cvat_password)

        if not is_cvat_configured:
            st.error(
                "CVAT hasn't configured, please configure it in the Control Panel page")
            return

        cvat_host = st.session_state.cvat_host
        cvat_username = st.session_state.cvat_username
        cvat_password = st.session_state.cvat_password

        # initiate dataset
        st.session_state.cvat_dataset = cvat.CVAT(
            username=cvat_username,
            password=cvat_password,
            host=cvat_host,
            dump_dir=dump_dir,
        )
        # download dataset
        st.session_state.cvat_dataset.tasks_dump(
            task_id=task_id,
            fileformat="COCO 1.0",
            filename=f"{task_id}.zip",
            extract=True,
            remove_zip=True,
            to_fiftyone=True
        )
        st.success(f"Download Dataset Task {task_id}")
        # # apply nms
        label_path = os.path.join(dataset_dir, "labels.json")
        utils.apply_nms(
            label_path=label_path,
            iou_threshold=float(iou_thres),
            dump_json=True,
        )
        st.success("Apply NMS")

        def open_new_tab(url):
            js = f"window.open('{url}')"
            html = '<img src onerror="{}">'.format(js)
            div = Div(text=html)
            st.bokeh_chart(div)

        if with_embd == "True":
            # load datasset to fiftyone
            st.session_state.dataset = fiftyone51.load_fiftyone(
                dataset_name=task_id,
                dataset_dir=dataset_dir,
                delete_existing=True,
                url='http://192.168.103.67:6001/delete/cache'
            )

            path_embedding = f'http://192.168.103.67:6001/embedding/{task_id}'
            path_fiftyone = f'http://192.168.103.67:6001/fiftyone/{task_id}'

            st.success(f"Embedding is available on {path_embedding}.")
            st.success(f"Fiftyone is available on {path_fiftyone}.")

            open_new_tab(path_embedding)
            open_new_tab(path_fiftyone)
        else:
            # preview to fiftyone
            st.session_state.dataset, st.session_state.patches = fiftyone51.preview_fiftyone(
                dataset_name=task_id,
                dataset_dir=dataset_dir,
                delete_existing=True,
                is_patches=True,
                port=port,
            )

            path_fiftyone = f'http://192.168.103.67:{port}/datasets/{task_id}'
            st.success(f"Fiftyone is available on {path_fiftyone}.")
            open_new_tab(path_fiftyone)

    if save_tags_btn:
        # save patches tags
        if with_embd == "True":
            patches = st.session_state.dataset.to_patches('ground_truth')
            st.session_state.tags = fiftyone51.get_tags(patches=patches)
        else:
            st.session_state.tags = fiftyone51.get_tags(
                patches=st.session_state.patches)

    if convert_btn:
        # convert labels
        fiftyone51.convert_labels(
            dataset_dir=dataset_dir,
            from_tag=from_tag,
            to_label=to_label,
            list_tags=st.session_state.tags,
            category_id=classes
        )
        # send back new labels to cvat
        st.session_state.cvat_dataset.tasks_upload(
            task_id=task_id,
            fileformat="COCO 1.0",
            filename=os.path.join(dataset_dir, "labels.json")
        )
        st.success(f"Success Evaluate Label Task #{task_id}")


if __name__ == "__main__":
    post_annotations(
        dump_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump"
    )
