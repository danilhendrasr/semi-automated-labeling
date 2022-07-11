""" Utils section """

import streamlit as st

from function.utils import apply_nms, parse_coco, xywh2xyxy


def apply_nms_section(section_key: str):
    st.subheader("Apply Non-Max Suppression")
    col = st.columns([2, 2, 1])
    with col[0]:
        username = st.text_input(
            label="Username", value="superadmin", key=f"{section_key}_apply_nms"
        )
    with col[1]:
        password = st.text_input(
            label="Password",
            value="KECILSEMUA",
            key=f"{section_key}_apply_nms",
            type="password",
        )
    with col[2]:
        task_id = st.text_input(
            label="Task Id", value="41", key=f"{section_key}_apply_nms"
        )
    btn = st.button(label="Apply NMS", key=f"{section_key}_apply_nms")

    return [username, password, task_id, btn]
