import streamlit as st
import os
from utils import DeployModel

def main():
    # title
    st.title('CVAT Model Deployment')

    # model repo
    st.header('Choose Model Repository')
    repo_type = st.radio('Repository Availability: ', ('Public', 'Private'))
    cols01, cols02 = st.columns(2)
    with cols01:
        repo = st.text_input("Repository")
    with cols02:
        branch = st.text_input("Branch", "main")
    token = None
    if repo_type == 'Private':
        token = st.text_input('Token')

    # init model deployment
    Deployment = DeployModel(
        url=repo,
        remote='/home/intern-didir/Repository/labelling/apps/cvat',
        branch=branch,
        token=token,
        gpu=False,
        )

    # clone repository
    clone_btn = st.button("Clone")
    if clone_btn:
        if repo_type == 'Private':
            Deployment.clone_repo()
            st.success('Sucess Clone Private Repository')
        else:
            Deployment.clone_repo()
            st.success('Sucess Clone Repository')

    # list of model
    st.subheader("List Model")
    st.write(os.listdir('/home/intern-didir/Repository/labelling/apps/cvat/serverless'))

    # deploy
    st.header('Deploy Model')
    st.markdown('Make sure in the repository there are `function.yaml` and `main.py`')

    deploy = st.button('Deploy Model')
    if deploy:
        Deployment.deploy_model()

if __name__ == "__main__":
    main()