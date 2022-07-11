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


if menu == "Control Panel":
    configs()

if menu == "Model Registry":
    model_registry()

if menu == "Model Deployment":
    model_deployment()

if menu == "Dataset Upload":
    dataset_upload()

if menu == "Dataset Splitter":
    dataset_splitter()

if menu == "Dataset Quality":
    dataset_quality()

if menu == "Label Evaluator":
    post_annotations()

if menu == "Dataset Versioning":
    dataset_versioning()
