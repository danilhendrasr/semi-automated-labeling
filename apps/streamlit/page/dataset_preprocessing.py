import streamlit as st
import section

### Dataset Preprocessing ###


def dataset_preprocessing(page_key):
    st.header('Dataset Preprocessing')
    section.repository(section_key=f'{page_key} repository')
    section.preprocessing('source', 'target', [
                          'None', 'Grayscale', 'Resize', 'Scale', 'Filter by size'], section_key=f'{page_key} preprocessinng')
