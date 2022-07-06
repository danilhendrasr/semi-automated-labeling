"""Control panel configurations"""

import sys
import os
import streamlit as st
import json

from function.configs import cleanup_dump_dir, init_git_config

# fmt: off
sys.path.append(os.path.abspath('../..'))
import apps.dash.config as dash_config
# fmt: on


def configs(page_key: str = "configs"):

    # state
    if "username" not in st.session_state:
        st.session_state.username = None
    if "email" not in st.session_state:
        st.session_state.email = None
    if "dump_dir" not in st.session_state:
        st.session_state.dump_dir = None
    if "fiftyone_port" not in st.session_state:
        st.session_state.fiftyone_port = None
    if "plotly_port" not in st.session_state:
        st.session_state.plotly_port = None
    if "dash_port" not in st.session_state:
        st.session_state.dash_port = None
    if "cvat_host" not in st.session_state:
        st.session_state.cvat_host = None
    if "cvat_username" not in st.session_state:
        st.session_state.cvat_username = None
    if "cvat_password" not in st.session_state:
        st.session_state.cvat_password = None

    st.header("Control Panel Configurations")

    st.subheader("CVAT")
    cvat_host = st.text_input("Host", placeholder="http://192.1.1.1:1111")
    st.session_state.cvat_host = cvat_host

    col_cvat = st.columns([1, 1])
    with col_cvat[0]:
        cvat_username = st.text_input(
            label="Username", placeholder="superadmin")
        st.session_state.cvat_username = cvat_username

    with col_cvat[1]:
        cvat_password = st.text_input(
            label="Password",
            type="password",
            placeholder="xxxxx"
        )
        st.session_state.cvat_password = cvat_password

    st.subheader("Github Account")
    col0 = st.columns([2, 2, 1])
    with col0[0]:
        username = st.text_input(
            label="Github username",
            value=st.session_state.username,
            key=page_key,
        )
        st.session_state.username = username
    with col0[1]:
        email = st.text_input(
            label="Github email",
            value=st.session_state.email,
            key=page_key,
        )
        st.session_state.email = email
    with col0[2]:
        st.write("Initialize Github")
        github_btn = st.button(
            label="Initialize",
            key=f"{page_key}_github_btn",
        )

    # button action
    if github_btn:
        init_git_config(username, email)
        with st.spinner("Initializing Github configs..."):
            st.success("Github configs initialized")

    st.subheader("Dump Directory")
    col1 = st.columns(2)
    with col1[0]:
        dump_dir = st.text_input(
            label="Dump Directory",
            value=st.session_state.dump_dir,
            key=page_key,
        )
        st.session_state.dump_dir = dump_dir
    with col1[1]:
        st.write("Cleanup Dump Directory")
        cleanup_btn = st.button(
            label="Cleanup",
            key=page_key,
        )
    if cleanup_btn:
        cleanup_dump_dir(dump_dir)
        with st.spinner("Cleaning up dump directory..."):
            st.success("Dump directory cleaned up")

    st.subheader("Port Configs")
    col2 = st.columns([2, 2, 2, 2, 2])
    with col2[0]:
        fiftyone_port = st.text_input(
            label="FiftyOne Port",
            value=st.session_state.fiftyone_port,
            key=page_key,
        )
        st.session_state.fiftyone_port = fiftyone_port
    with col2[1]:
        flask_port = dash_config.port['flask']
        st.selectbox(
            label="Flask Port",
            options=[flask_port],
            key=page_key,
        )
        st.session_state.flask_port = flask_port
    with col2[2]:
        dash_port = dash_config.port['dash']
        st.selectbox(
            label="Dash Port",
            options=[dash_port],
            key=page_key
        )
        st.session_state.dash_port = dash_port
    with col2[3]:
        st.write("Save Configs")
        save_btn = st.button(
            label="Save",
            key=f"{page_key}_save_btn",
        )
    if save_btn:
        json_configs = {
            "username": username,
            "email": email,
            "dump_dir": dump_dir,
            "fiftyone_port": fiftyone_port,
            "flask_port": flask_port,
            "dash_port": dash_port,
        }
        json_object = json.dumps(json_configs, indent=4)

        with open(os.path.join(dump_dir, 'configs.json'), 'w') as f:
            f.write(json_object)

        st.success(f"Configs saved in {dump_dir}")

    return [dump_dir, fiftyone_port, flask_port, dash_port]
