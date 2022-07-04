from page.dataset_splitter import dataset_splitter
from page.model_registry import model_registry
from page.model_deployment import model_deployment
from page.post_annotations import post_annotations
from page.dataset_versioning import dataset_versioning
from page.dataset_quality import dataset_quality
from page.dataset_upload import dataset_upload

import streamlit as st
from streamlit_option_menu import option_menu

with st.sidebar:
    menu = option_menu(
        "Main Menu",
        [
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
        default_index=1,
    )

if menu == "Model Registry":
    model_registry()

if menu == "Model Deployment":
    model_deployment(
        dump_dir="./dump"
    )

if menu == "Dataset Upload":
    dataset_upload(page_key="Dataset Upload")

if menu == "Dataset Splitter":
    dataset_splitter(
        dump_dir="./dump"
    )

if menu == "Dataset Quality":
    dataset_quality(
        dump_dir="./dump",
        port=7101,
    )

if menu == "Label Evaluator":
    post_annotations(
        dump_dir="./dump",
        port=7101,
    )

if menu == "Dataset Versioning":
    dataset_versioning(
        dump_dir="./dump"
    )
