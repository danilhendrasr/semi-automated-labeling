"""Dataset Qualitry"""

import streamlit as st
import os

from function.validac import Validac
from function.cvat import CVAT


def dataset_quality(page_key: str = "dataset_quality", dump_dir: str = os.getcwd(), port: int = 6161):
    """Dataset Quality"""

    # state
    if "cvat" not in st.session_state:
        st.session_state.cvat = None
    if "validac" not in st.session_state:
        st.session_state.validac = None
    if "validac" not in st.session_state:
        st.session_state.validac = None

    st.header("Dataset Quality")
    st.write("Feature Dataset Quality berfungsi untuk mengevaluasi dataset predictions \
            dengan dataset ground-truth. Metric yang digunakan dalam evaluasi adalah mAP. \
            Hasil evaluasi juga selanjutnya dapat ditampilkan di FiftyOne.")

    st.subheader("CVAT Authentications")
    col0 = st.columns([2, 2])
    with col0[0]:
        username = st.text_input(
            label="Username", value="superadmin", key=f"{page_key}"
        )
    with col0[1]:
        password = st.text_input(
            label="Password", value="KECILSEMUA", key=f"{page_key}", type="password"
        )

    st.subheader("Evaluate Predictions Task")
    col1 = st.columns([2, 2, 2])
    with col1[0]:
        gt_id = st.text_input(
            label="Task ID Dataset Ground Truth",
            value="52",
            key=f"{page_key}",
        )
    with col1[1]:
        pred_id = st.text_input(
            label="Task ID Dataset Predictions",
            value="51",
            key=f"{page_key}",
        )
    with col1[2]:
        iou = st.text_input(
            label="IoU Threshold",
            value="0.5",
            key=f"{page_key}",
        )

    col2 = st.columns([1, 2, 3])
    with col2[0]:
        evaluate = st.button(label="Evaluate")
    with col2[1]:
        preview = st.button(label="Preview in Fiftyone")

    if evaluate:
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
        results = st.session_state.validac.compute_results()
        # mean average precision
        mAP = st.session_state.validac.compute_mAP()
        # dataset stats
        stats = st.session_state.validac.stats()

        # generate metrics
        col3 = st.columns([1, 1, 1, 1])
        with col3[0]:
            st.metric(label="mAP", value=round(mAP, 4))
        with col3[1]:
            st.metric(label="Total Images", value=stats[0])
        with col3[2]:
            st.metric(label="Total Annotations (Pred)", value=stats[1])
        with col3[3]:
            st.metric(label="Dataset Size", value=stats[2])

        # conf matrix and embeddings
        col4 = st.columns([1, 1])
        with col4[0]:
            # plot confusion matrix
            st.write("Confusion Matrix")
            conf_mtx = st.session_state.validac.confusion_matrix()
            st.pyplot(conf_mtx)
        with col4[1]:
            # plot embedding
            st.write("Prediction Embedding")
            st.session_state.validac.embedding()
            st.image(os.path.join(dump_dir, "embedding.png"))

        # distribution
        col5 = st.columns([1, 1])
        with col5[0]:
            # plot distribution
            st.write("Ground Truth Distribution")
            st.session_state.validac.gt_distribution()
            st.image(os.path.join(dump_dir, "gt_distribution.png"))
        with col5[1]:
            # plot distribution
            st.write("Predictions Distribution")
            st.session_state.validac.pred_distribution()
            st.image(os.path.join(dump_dir, "pred_distribution.png"))

    if preview:
        """preview evaluation to fiftyone"""
        st.session_state.validac.preview_evaluation(port=port)
