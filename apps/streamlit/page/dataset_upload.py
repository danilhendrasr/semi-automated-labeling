import os
import zipfile
import streamlit as st

from function.repository import Repository
from function.cvat import CVAT


# TODO:
# 1. Clear form on submit
# 2. Segment size
# 3. Batch upload
def dataset_upload(dump_dir: str = os.getcwd()):
    """ Code for dataset upload page """

    st.header("Dataset Upload")

    st.subheader("Repository Creation")
    cols = st.columns([1, 1])
    with cols[0]:
        repo_url = st.text_input(
            label="Repository URL", placeholder="https://github.com/username/repository", value="https://github.com/danilhendrasr/tryp")

    with cols[1]:
        access_token = st.text_input(
            label='Personal Access Token',
            value='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',
            type='password')

    cols_2 = st.columns([3, 2, 1])

    with cols_2[0]:
        repo_description = st.text_input(
            label="Short Description (Optional)", placeholder="Dataset repo")

    with cols_2[1]:
        initial_dataset_tag = st.text_input(
            label='Initial Tag (Optional)',
            value='v0', placeholder="v0.0.0")

    with cols_2[2]:
        repo_visibility = st.selectbox(
            'Repo Visibility', ("Private", "Public"), index=0)

    file_upload = st.file_uploader(accept_multiple_files=False,
                                   label="Dataset File", type="zip")

    st.header("CVAT Metadata")

    cvat_task_name = st.text_input(
        label="Task Name", placeholder="CVAT Task Name", value="asdf")

    cvat_task_labels = st.text_input(
        label="Labels (Separate with comma)", placeholder="Cat,Dog,Car,Pedestrian")

    upload_btn = st.button(label="Upload")

    if upload_btn:
        is_cvat_configured = bool(st.session_state.cvat_host) and bool(
            st.session_state.cvat_username) and bool(st.session_state.cvat_password)

        if not is_cvat_configured:
            st.error(
                "CVAT hasn't configured, please configure it in the Control Panel page")
            return

        if not repo_url:
            st.error("Repository name cannot be empty")
            return

        if not access_token:
            st.error("Personal access token name cannot be empty")
            return

        if not cvat_task_name:
            st.error("CVAT task name cannot be empty")
            return

        if not cvat_task_labels:
            st.error("CVAT task labels cannot be empty")
            return

        if not file_upload:
            st.error("You haven't upload a dataset file")
            return

        if file_upload:
            with st.spinner("Processing..."):
                bytes_data = file_upload.getvalue()
                data_dir = f"{dump_dir}/dataset"

                repo = Repository(repo_url=repo_url, ref="main",
                                  token=access_token, dump_dir=dump_dir, with_dvc=True, init_remote={
                                      "description": repo_description if repo_description else "",
                                      "private": repo_visibility == "Private"
                                  })

                if not repo.successfuly_created:
                    st.error(
                        "Failed creating repo, see if GitHub is down, check personal access token, and then try again.")
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
                            files_to_push.append(f"{data_dir}/{x}")
                        else:
                            target = f"{data_dir}/{x}"
                            if os.path.isdir(target):
                                os.removedirs(target)
                            else:
                                os.remove(target)

                    if len(files_to_push) == 0:
                        st.error("Cannot upload empty dataset")
                        return

                    repo.commit(git_items=[".gitignore", "dataset.dvc"],
                                dvc_items=["dataset"],
                                message="initial dataset version")

                    if initial_dataset_tag:
                        repo.tag(initial_dataset_tag, False)

                    repo.push(with_dataset=True)

                    cvat_host = st.session_state.cvat_host
                    cvat_username = st.session_state.cvat_username
                    cvat_password = st.session_state.cvat_password

                    st.session_state.cvat_dataset = CVAT(
                        username=cvat_username, password=cvat_password, host=cvat_host, dump_dir=dump_dir)

                    task_labels = [{"name": x}
                                   for x in cvat_task_labels.split(",")]
                    new_task_id = st.session_state.cvat_dataset.tasks_create(
                        name=cvat_task_name, labels=task_labels, resource_type="local", resources=files_to_push)

                    new_task_url = f"{cvat_host}/tasks/{new_task_id}"
                    st.success(
                        f"Success, dataset repository can be accessed at {repo_url} and CVAT task can be accessed at {new_task_url}")
