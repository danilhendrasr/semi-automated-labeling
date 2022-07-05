import os
import zipfile
from fsutil import is_dir
import streamlit as st
import shutil

from function.repository import Repository
from function.cvat import CVAT


# TODO: Handle cannot create dataset repo
def dataset_upload(page_key: int):
    """ Code for dataset upload page """

    st.header("Dataset Upload")

    st.subheader("Repository Creation")
    cols = st.columns([3, 2, 1, 1])
    with cols[0]:
        repo_url = st.text_input(
            label="Repository URL \n (a new repo will be created in this URL)", placeholder="https://github.com/username/repository")

    with cols[1]:
        gh_token = st.text_input(
            label='Personal Access Token',
            value='xxx',
            type='password')

    with cols[2]:
        branch = st.text_input(
            label='Branch',
            value='main')

    with cols[3]:
        tag = st.text_input(
            label='Tag',
            value='v0')

    file_upload = st.file_uploader(accept_multiple_files=False,
                                   label="Dataset File", type="zip")
    st.header("CVAT Configuration")

    col0 = st.columns([2, 2])
    with col0[0]:
        cvat_username = st.text_input(
            label="Username", value="superadmin", key=f"{page_key}_versioning"
        )
    with col0[1]:
        cvat_password = st.text_input(
            label="Password",
            value="KECILSEMUA",
            key=f"{page_key}_versioning",
            type="password",
        )

    cvat_task_name = st.text_input(
        label="Task Name", placeholder="CVAT Task Name")

    upload_btn = st.button(label="Upload")

    if upload_btn:
        if repo_url is None:
            st.error("Repository name cannot be empty")

        if file_upload is not None:
            with st.spinner("Processing..."):
                bytes_data = file_upload.getvalue()
                new_repo_dir = "/tmp/dataset-upload"
                data_dir = f"{new_repo_dir}/dataset"

                repo = Repository(repo_url=repo_url, ref=branch,
                                  token=gh_token, dump_dir=new_repo_dir, with_dvc=True, init_remote={
                                      "description": "Testing dataset upload",
                                      "private": True
                                  })

                if not repo.successfuly_created:
                    st.error(
                        "Failed creating repo, please retry in a few minutes.")
                    return

                repo_dir = repo.repo_dir
                data_dir = f"{repo_dir}/dataset"
                if not os.path.exists(data_dir):
                    # shutil.rmtree(data_dir)
                    os.makedirs(data_dir)

                file = open(f'{data_dir}/data.zip', 'wb')
                file.write(bytes_data)
                file.close()

                with zipfile.ZipFile(f'{data_dir}/data.zip') as zip_obj:
                    # Handle if there are non-image files in the zip
                    zip_obj.extractall(path=data_dir)
                    os.remove(f"{data_dir}/data.zip")

                    files_to_push = []
                    # Remove files with extensions other than .jpg, .jpeg, or .png
                    for x in os.listdir(data_dir):
                        filename = x.lower()
                        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                            files_to_push.append(f"{data_dir}/{filename}")
                        else:
                            target = f"{data_dir}/{filename}"
                            if is_dir(target):
                                os.removedirs(target)
                            else:
                                os.remove(target)

                    if len(files_to_push) == 0:
                        st.error("Cannot upload empty dataset")
                        return

                    repo.commit(git_items=[".gitignore", "dataset.dvc"],
                                dvc_items=["dataset"],
                                message="initial dataset version")
                    repo.tag(tag, False)
                    repo.push()

                    cvat_host = "http://192.168.103.67:8080"
                    if 'cvat_dataset' not in st.session_state:
                        st.session_state.cvat_dataset = CVAT(
                            username=cvat_username, password=cvat_password, host=cvat_host, dump_dir="/tmp/dataset-upload/dump")

                    new_task_id = st.session_state.cvat_dataset.tasks_create(name=cvat_task_name, labels=[
                        {"name": "Dummy"}], resource_type="local", resources=files_to_push)

                    new_task_url = f"{cvat_host}/{new_task_id}"
                    st.success(
                        f"Success, dataset repository can be accessed at {repo_url} and CVAT task can be accessed at {new_task_url}")
