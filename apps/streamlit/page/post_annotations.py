""" Post Annotations Page """

import os
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

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
    except:
        classes = []

    st.header("Post Annotations")
    st.subheader("Get Dataset")

    col = st.columns([2, 2, 1, 1])
    with col[0]:
        username = st.text_input(label="Username", value="superadmin")
    with col[1]:
        password = st.text_input(
            label="Password",
            value="KECILSEMUA",
            type="password",
        )
    with col[2]:
        iou_thres = st.text_input(label="IoU Threshold", value="0.5")
    with col[3]:
        task_id = st.text_input(label="Task Id", value="39")

    # init dataset directory
    dataset_dir = os.path.join(dump_dir, task_id)

    col1 = st.columns([2, 2, 1, 1])
    with col1[0]:
        btn = st.button(label="Preview in FiftyOne")
    with col1[1]:
        save_tags_btn = st.button(label="Save Tags")

    st.subheader("Changes Labels")
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
    convert_btn = st.button(label="Convert")

    st.subheader("Send Back to CVAT")
    send_to_cvat_btn = st.button(label="Send Back to CVAT")

    if btn:
        # initiate dataset
        st.session_state.cvat_dataset = cvat.CVAT(
            username=username,
            password=password,
            host="http://192.168.103.67:8080",
            dump_dir=dump_dir,
        )
        # download dataset
        st.session_state.cvat_dataset.tasks_dump(
            task_id=task_id,
            fileformat="COCO 1.0",
            filename=f"{task_id}.zip",
            extract=True,
        )
        st.success(f"Download Dataset Task {task_id}")
        # # apply nms
        label_path = os.path.join(dataset_dir, "annotations", "instances_default.json")
        utils.apply_nms(
            label_path=label_path,
            iou_threshold=float(iou_thres),
            dump_json=True,
        )
        st.success("Apply NMS")
        # # convert to fiftyone COCO
        fiftyone51.convert_to_coco(dataset_dir=dataset_dir)
        # preview to fiftyone
        st.session_state.dataset, st.session_state.patches = fiftyone51.preview_fiftyone(
            dataset_name=task_id,
            dataset_dir=dataset_dir,
            delete_existing=True,
            port=port,
        )
        st.success("Preview to FiftyOne")
    
    if save_tags_btn:
        # save patches tags
        st.session_state.tags = fiftyone51.get_tags(patches=st.session_state.patches)

    if convert_btn:
        # convert labels
        fiftyone51.convert_labels(
            dataset_dir=dataset_dir,
            from_tag=from_tag,
            to_label=to_label,
            list_tags=st.session_state.tags,
            category_id=classes
        )

    if send_to_cvat_btn:
        # send back new labels to cvat
        st.session_state.cvat_dataset.tasks_upload(
            task_id=task_id,
            fileformat="COCO 1.0",
            filename=os.path.join(dataset_dir, "labels_new.json")
        )

if __name__ == "__main__":
    post_annotations(
        dump_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump"
    )


# def post_annotations(
#     page_key: str = "post_annotations", dump_dir: str = os.getcwd(), port: int = 5151
# ):

#     st.header("Post Annotations")
#     username, password, iou_thres, task_id, btn = sec_cvat.export_dataset_fiftyone(
#         section_key=page_key
#     )
#     dataset_dir = os.path.join(dump_dir, task_id)

#     # TODO: change to section
#     st.subheader("Review in CVAT")
#     review_btn = st.button("Review in CVAT")

#     # init ids
#     if "list_ids" not in st.session_state:
#         st.session_state.list_ids = []

#     if "index" not in st.session_state:
#         st.session_state.index = 0

#     if "patches" not in st.session_state:
#         st.session_state.patches = None

#     if "dataset" not in st.session_state:
#         st.session_state.dataset = None

#     col = st.columns([10, 1, 2, 1, 10])

#     with col[1]:
#         prev_btn = st.button("Prev")
#     with col[2]:
#         ids_view = st.selectbox(label="Frame Id", options=st.session_state.list_ids)
#     with col[3]:
#         next_btn = st.button("Next")

#     if prev_btn:
#         components.iframe(
#             src=f"http://192.168.103.67:8080/tasks/39/jobs/18?frame={st.session_state.list_ids[st.session_state.index]}",
#             height=800,
#         )
#         st.session_state.index -= 1

#     if next_btn:
#         components.iframe(
#             src=f"http://192.168.103.67:8080/tasks/39/jobs/18?frame={st.session_state.list_ids[st.session_state.index]}",
#             height=800,
#         )
#         st.session_state.index += 1

#     if btn:
#         dataset = cvat.CVAT(
#             username=username,
#             password=password,
#             host="http://192.168.103.67:8080",
#             dump_dir=dump_dir,
#         )
#         st.session_state.dataset = dataset

#         dataset.tasks_dump(
#             task_id=task_id,
#             fileformat="COCO 1.0",
#             filename=f"{task_id}.zip",
#             extract=True,
#         )
#         st.success(f"[INFO] Download Dataset Task {task_id}")

#         # apply nms
#         # TODO: maybe create another page/section
#         json_file_path = os.path.join(
#             dataset_dir, "annotations", "instances_default.json"
#         )
#         annots, scores = utils.parse_coco(json_file=json_file_path)
#         utils.apply_nms(
#             json_file=json_file_path,
#             annotations=annots,
#             scores=scores,
#             iou_threshold=float(iou_thres),
#             dump_json=True,
#         )
#         st.success("[INFO] Apply NMS")

#         fiftyone51.convert_to_coco(dataset_dir=dataset_dir)
#         st.success("[INFO] Convert to FiftyOne COCO Format")

#         dataset_51, patches = fiftyone51.preview_fiftyone(
#             dataset_name=task_id,
#             dataset_dir=dataset_dir,
#             delete_existing=True,
#             port=port,
#         )
#         st.session_state.patches = patches
#         st.success("[INFO] Load to FiftyOne")

#     if review_btn:
#         index = fiftyone51.save_tags_patches(
#             patches=st.session_state.patches, dataset_dir=dataset_dir
#         )
#         st.session_state.list_ids.append(index)

#         # upload to cvat
#         st.session_state.dataset.tasks_upload(
#             task_id=task_id,
#             fileformat="COCO 1.0",
#             filename=os.path.join(dataset_dir, "labels.json"),
#         )
