"""Control panel configurations"""

import sys
import os
import streamlit as st

from function.configs import cleanup_dump_dir, init_git_config

# fmt: off
sys.path.append(os.path.abspath('../..'))
import apps.dash.config as dash_config
# fmt: on

def configs(page_key: str = "configs"):

    # state
    if "username" not in st.session_state:
        st.session_state.username = "Didi Ruhyadi"
    if "email" not in st.session_state:
        st.session_state.email = "ruhyadi.dr@gmail.com"
    if "dump_dir" not in st.session_state:
        st.session_state.dump_dir = "/tmp"
    if "serverless_dir" not in st.session_state:
        st.session_state.serverless_dir = "/home/apps/cvat/serverless"
    if "fiftyone_port" not in st.session_state:
        st.session_state.fiftyone_port = "7101"
    # if "plotly_port" not in st.session_state:
    #     st.session_state.plotly_port = None
    # if "dash_port" not in st.session_state:
    #     st.session_state.dash_port = None
    if "cvat_host" not in st.session_state:
        st.session_state.cvat_host = "http://192.168.103.67:8080"
    if "cvat_username" not in st.session_state:
        st.session_state.cvat_username = "superadmin"
    if "cvat_password" not in st.session_state:
        st.session_state.cvat_password = "KECILSEMUA"

    st.header("Control Panel Configurations")

    st.subheader("CVAT Authentications")
    cvat_host = st.text_input(
        label="Host",
        value=st.session_state.cvat_host,
        key=f"{page_key}_cvat_host",
        )
    st.session_state.cvat_host = cvat_host

    col_cvat = st.columns([1, 1])
    with col_cvat[0]:
        cvat_username = st.text_input(
            label="Username", 
            value=st.session_state.cvat_username, 
        )
        st.session_state.cvat_username = cvat_username
    with col_cvat[1]:
        cvat_password = st.text_input(
            label="Password",
            value=st.session_state.cvat_password,
            type="password",
        )
        st.session_state.cvat_password = cvat_password

    st.subheader("Git Configuration")
    col0 = st.columns([2, 2])
    with col0[0]:
        username = st.text_input(
            label="Git username",
            value=st.session_state.username,
            key=page_key,
        )
        st.session_state.username = username
    with col0[1]:
        email = st.text_input(
            label="Git email",
            value=st.session_state.email,
            key=page_key,
        )
        st.session_state.email = email

    st.subheader("Directory Configurations")
    col1 = st.columns([2, 2, 1])
    with col1[0]:
        serverless_dir = st.text_input(
            label="Serverless Directory",
            value=st.session_state.serverless_dir,
            key=page_key
        ) 
        st.session_state.serverless_dir = serverless_dir
    with col1[1]:
        dump_dir = st.text_input(
            label="Dump Directory",
            value=st.session_state.dump_dir,
            key=page_key,
        )
        st.session_state.dump_dir = dump_dir
    with col1[2]:
        st.write("Cleanup")
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

    col3 = st.columns([6, 2])
    with col3[1]:
        save_btn = st.button(
            label="Save Configuration",
            key=page_key,
        )
    
    if save_btn:
        init_git_config(username, email)
        with st.spinner("Saving Configurations..."):
            st.success("Configurations saved")