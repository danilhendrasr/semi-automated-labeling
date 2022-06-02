import streamlit as st
import utils
st.title('Dataset Preprocessing')


st.subheader('Repository')

repository_col = st.columns([3, 1, 1])

with repository_col[0]: url = st.text_input('Repository URL')
with repository_col[1]: token = st.text_input('Token')
with repository_col[2]: tag = st.text_input('Tag')
repository = (url, token, tag)

repository_clone = st.button('Clone Repository')
if repository_clone:
    print('Clone Repository')


# ==============================================================================


st.subheader('Preprocess')

available_preprocess_list = [None] + utils.preprocess.get_names()

if 'num_preprocess' not in st.session_state:
    st.session_state.num_preprocess = 1

preprocess_col = st.columns([1, 2, 2])
with preprocess_col[0]: add_preprocess = st.button('Add Preprocess') 
with preprocess_col[1]: remove_preprocess = st.button('Remove Preprocess')

if add_preprocess: st.session_state.num_preprocess += 1
if remove_preprocess: st.session_state.num_preprocess = max(1, st.session_state.num_preprocess-1)
    
preprocess_list = []
for i in range(st.session_state.num_preprocess):
    preprocess = dict()
    preprocess['name'] = st.selectbox(f'Preprocess Function - {i+1}', available_preprocess_list)
    if not preprocess['name']: continue
    
    params = []
    columns = utils.preprocess.get_columns(preprocess['name'])
    if len(columns):
        params_col = st.columns(columns)
        for j, label in enumerate(utils.preprocess.get_labels(preprocess['name'])):
            with params_col[j]:
                value = st.text_input(label, key=f'Preprocess Function - {i+1} {label}')
                params.append({
                    'label' : label,
                    'value' : value
                })
        preprocess['params'] = params

    preprocess_list.append(preprocess)

preview = st.button('Preview')
if preview: utils.preprocess.preprocess(preprocess_list)


# ==============================================================================


send_to_cvat = st.button('Send to CVAT')
if send_to_cvat: print('send to cvat')