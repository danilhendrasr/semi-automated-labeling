from page.model_registry import model_registry
from page.model_deployment import model_deployment
from page.post_annotations import post_annotations
from page.dataset_versioning import dataset_versioning
from page.dataset_quality import dataset_quality

import streamlit as st

from streamlit_option_menu import option_menu

with st.sidebar:
    menu = option_menu(
        "Main Menu",
        [
            "Model Registry",
            "Model Deployment",
            "Dataset Quality",
            "Dataset Versioning",
            "Label Evaluator",
        ],
        icons=["house", "gear", "gear"],
        menu_icon="cast",
        default_index=1,
    )

if menu == "Model Registry":
    model_registry()

if menu == "Model Deployment":
    model_deployment(
        dump_dir="/home/intern-didir/Repository/labelling/apps/cvat/serverless"
    )

if menu == "Dataset Quality":
    dataset_quality(
        dump_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump"
    )

if menu == "Dataset Versioning":
    dataset_versioning(
        dump_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump"
    )

if menu == "Label Evaluator":
    post_annotations(
        dump_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump", 
        port=6161
    )