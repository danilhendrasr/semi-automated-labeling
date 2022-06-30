from page.model_registry import model_registry
from page.model_deployment import model_deployment
from page.post_annotations import post_annotations
from page.dataset_versioning import dataset_versioning

import streamlit as st

from streamlit_option_menu import option_menu

with st.sidebar:
    menu = option_menu(
        "Main Menu",
        [
            "Model Registry",
            "Model Deployment",
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

if menu == "Dataset Versioning":
    dataset_versioning(
        dump_dir="./dump"
    )

if menu == "Label Evaluator":
    post_annotations(
        dump_dir="./dump", 
        port=6161
    )