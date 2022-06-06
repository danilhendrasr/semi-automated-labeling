import streamlit as st
import section

def dataset_preprocessing(page_key):
    st.header('Dataset Preprocessing')
    section.repository(section_key=f'{page_key} repository')
    section.preprocessing('source', 'target', ['None', 'grayscale', 'resize', 'scale'], section_key=f'{page_key} preprocessinng')