import streamlit as st

def repository(section_key):
    st.subheader('Repository')
    col = st.columns([3, 1, 1])
    with col[0]: url = st.text_input('Repository URL', key=f'{section_key} input url')
    with col[1]: token = st.text_input('Token', key=f'{section_key} input token')
    with col[2]: tag = st.text_input('Tag/Branch', key=f'{section_key} input tag')
    return url, token, tag