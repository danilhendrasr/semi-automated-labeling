""" Post Annotations Page """

import os
import streamlit as st
import streamlit.components.v1 as components
from section import cvat as sec_cvat

from function import fiftyone51
from function import cvat
from function import utils


def post_annotations(
    page_key: str = "post_annotations", dump_dir: str = os.getcwd(), port: int = 5151
):

    st.header("Post Annotations")
    username, password, iou_thres, task_id, btn = sec_cvat.export_dataset_fiftyone(
        section_key=page_key
    )
    dataset_dir = os.path.join(dump_dir, task_id)

    # TODO: change to section
    st.subheader("Review in CVAT")
    review_btn = st.button("Review in CVAT")

    # init ids
    if "list_ids" not in st.session_state:
        st.session_state.list_ids = []

    if "index" not in st.session_state:
        st.session_state.index = 0

    if "patches" not in st.session_state:
        st.session_state.patches = None

    if "dataset" not in st.session_state:
        st.session_state.dataset = None

    col = st.columns([10, 1, 2, 1, 10])

    with col[1]:
        prev_btn = st.button("Prev")
    with col[2]:
        ids_view = st.selectbox(label="Frame Id", options=st.session_state.list_ids)
    with col[3]:
        next_btn = st.button("Next")

    if prev_btn:
        components.iframe(
            src=f"http://192.168.103.67:8080/tasks/39/jobs/18?frame={st.session_state.list_ids[st.session_state.index]}",
            height=800,
        )
        st.session_state.index -= 1

    if next_btn:
        components.iframe(
            src=f"http://192.168.103.67:8080/tasks/39/jobs/18?frame={st.session_state.list_ids[st.session_state.index]}",
            height=800,
        )
        st.session_state.index += 1

    if btn:
        dataset = cvat.CVAT(
            username=username,
            password=password,
            host="http://192.168.103.67:8080",
            dump_dir=dump_dir,
        )
        st.session_state.dataset = dataset

        dataset.tasks_dump(
            task_id=task_id,
            fileformat="COCO 1.0",
            filename=f"{task_id}.zip",
            extract=True,
        )
        st.success(f"[INFO] Download Dataset Task {task_id}")

        # apply nms
        # TODO: maybe create another page/section
        json_file_path = os.path.join(
            dataset_dir, "annotations", "instances_default.json"
        )
        annots, scores = utils.parse_coco(json_file=json_file_path)
        utils.apply_nms(
            json_file=json_file_path,
            annotations=annots,
            scores=scores,
            iou_threshold=float(iou_thres),
            dump_json=True,
        )
        st.success("[INFO] Apply NMS")

        fiftyone51.convert_to_coco(dataset_dir=dataset_dir)
        st.success("[INFO] Convert to FiftyOne COCO Format")

        dataset_51, patches = fiftyone51.preview_fiftyone(
            dataset_name=task_id,
            dataset_dir=dataset_dir,
            delete_existing=True,
            port=port,
        )
        st.session_state.patches = patches
        st.success("[INFO] Load to FiftyOne")

    if review_btn:
        index = fiftyone51.save_tags_patches(
            patches=st.session_state.patches, dataset_dir=dataset_dir
        )
        st.session_state.list_ids.append(index)

        # upload to cvat
        st.session_state.dataset.tasks_upload(
            task_id=task_id,
            fileformat="COCO 1.0",
            filename=os.path.join(dataset_dir, "labels.json"),
        )
