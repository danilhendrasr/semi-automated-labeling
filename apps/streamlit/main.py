from page.configs import configs
from streamlit_option_menu import option_menu
import streamlit as st
from page.dataset_upload import dataset_upload
from page.dataset_quality import dataset_quality
from page.dataset_versioning import dataset_versioning
from page.post_annotations import post_annotations
from page.model_deployment import model_deployment
from page.model_registry import model_registry
from page.dataset_splitter import dataset_splitter

with st.sidebar:
    menu = option_menu(
        "Main Menu",
        [
            "Control Panel",
            "Model Registry",
            "Model Deployment",
            "Dataset Upload",
            "Dataset Splitter",
            "Dataset Quality",
            "Label Evaluator",
            "Dataset Versioning",
        ],
        icons=["house", "robot", "images", "eye", "patch-check", "patch-plus"],
        menu_icon="cast",
        default_index=0,
    )

# session state
if "dump_dir" not in st.session_state:
    st.session_state.dump_dir = None
if "fiftyone_port" not in st.session_state:
    st.session_state.fiftyone_port = None
if "plotly_port" not in st.session_state:
    st.session_state.plotly_port = None
if "dash_port" not in st.session_state:
    st.session_state.dash_port = None

if menu == "Control Panel":
    configurations = configs()
    st.session_state.cvat_host = configurations[0]
    st.session_state.cvat_username = configurations[1]
    st.session_state.cvat_password = configurations[2]
    st.session_state.dump_dir = configurations[3]
    st.session_state.fiftyone_port = configurations[4]
    st.session_state.plotly_port = configurations[5]
    st.session_state.dash_port = configurations[6]

if menu == "Model Registry":
    model_registry(dump_dir=st.session_state.dump_dir)

if menu == "Model Deployment":
    model_deployment(dump_dir=st.session_state.dump_dir)

if menu == "Dataset Upload":
    dataset_upload(dump_dir=st.session_state.dump_dir)

if menu == "Dataset Splitter":
    dataset_splitter(dump_dir=st.session_state.dump_dir)

if menu == "Dataset Quality":
    dataset_quality(dump_dir=st.session_state.dump_dir,
                    port=st.session_state.fiftyone_port)

if menu == "Label Evaluator":
    post_annotations(dump_dir=st.session_state.dump_dir,
                     port=st.session_state.fiftyone_port)

if menu == "Dataset Versioning":
    dataset_versioning(dump_dir=st.session_state.dump_dir)
