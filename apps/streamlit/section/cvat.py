import streamlit as st


def export_dataset_fiftyone(section_key: str):
    """
    export/download dataset (with annotations) from cvat task
    """

    st.subheader("Export Task Dataset")
    col = st.columns([2, 2, 1, 1])
    with col[0]:
        username = st.text_input(
            label="Username", value="superadmin", key=f"{section_key}_export_dataset_51"
        )
    with col[1]:
        password = st.text_input(
            label="Password",
            value="KECILSEMUA",
            key=f"{section_key}_export_dataset_51",
            type="password",
        )
    with col[2]:
        iou_thres = st.text_input(
            label="IoU Threshold", value="0.5", key=f"{section_key}_export_dataset_51"
        )
    with col[3]:
        task_id = st.text_input(
            label="Task Id", value="28", key=f"{section_key}_export_dataset_51"
        )

    btn = st.button(label="Fiftyone Preview",
                    key=f"{section_key}_export_dataset_51")

    return [username, password, iou_thres, task_id, btn]


def export_dataset(section_key: str):
    """
    export/download dataset (with annotations) from cvat task
    """

    st.subheader("Export Task Dataset")
    col0 = st.columns([2, 2])
    with col0[0]:
        username = st.text_input(
            label="Username", value="superadmin", key=f"{section_key}_export_dataset"
        )
    with col0[1]:
        password = st.text_input(
            label="Password",
            value="KECILSEMUA",
            key=f"{section_key}_export_dataset",
            type="password",
        )
    col1 = st.columns([2, 1, 2])
    with col1[0]:
        filename = st.text_input(
            label="Filename", value="sample.zip", key=f"{section_key}_export_dataset"
        )
    with col1[1]:
        task_id = st.text_input(
            label="Task Id", value="28", key=f"{section_key}_export_dataset"
        )
    with col1[2]:
        format = st.selectbox(
            label="Annotation Format",
            options=["COCO 1.0", "YOLO 1.1"],
            key=f"{section_key}_export_dataset",
        )

    btn = st.button(label="Download Dataset",
                    key=f"{section_key}_export_dataset")

    return [username, password, filename, task_id, format, btn]
