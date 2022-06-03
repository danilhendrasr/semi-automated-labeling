import streamlit as st
import section

def dataset_preprocessing(page_key):
    st.header('Dataset Preprocessing')
    section.preprocessing('path', ['None', 'grayscale', 'resize', 'scale'], section_key=f'{page_key} preprocessinng - 1')
    section.preprocessing('path', ['None', 'grayscale'], section_key=f'{page_key} preprocessing - 2')