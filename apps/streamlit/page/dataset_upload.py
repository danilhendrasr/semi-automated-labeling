import os
import zipfile
import streamlit as st
import section

from function.repository import Repository
from function.cvat import CVAT


# TODO: Handle cannot create dataset repo
def dataset_upload(page_key: int):
    """ Code for dataset upload page """

    st.header("Dataset Upload")
    repo_url, gh_token, ref = section.repository.clone(
        section_key=f'{page_key} repository')
    file_upload = st.file_uploader(accept_multiple_files=False,
                                   label="Dataset File", type="zip")
    upload_btn = st.button(label="Upload")

    branch, tag = ref.split("/")

    if upload_btn:
        if repo_url is None:
            st.write("Repo empty")

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

                repo_dir = repo.repo_dir
                data_dir = f"{repo_dir}/dataset"
                os.mkdir(data_dir)
                file = open(f'{data_dir}/data.zip', 'wb')
                file.write(bytes_data)
                file.close()

                with zipfile.ZipFile(f'{data_dir}/data.zip') as zip_obj:
                    # Handle if there are non-image files in the zip
                    zip_obj.extractall(path=data_dir)
                    os.remove(f"{data_dir}/data.zip")

                    # repo.commit(git_items=[".gitignore", "dataset.dvc"],
                    #             dvc_items=["dataset"],
                    #             message="initial dataset version")
                    # repo.tag(tag, False)
                    # repo.push()

                    if 'cvat_dataset' not in st.session_state:
                        st.session_state.cvat_dataset = CVAT(username="superadmin", password="KECILSEMUA",
                                                             host="http://192.168.103.67:8080/", dump_dir="/workspaces/semi-automated-labeling/dump")

                    print(st.session_state.cvat_dataset.tasks_list())
                    st.session_state.cvat_dataset.tasks_create(name="Heytayo", labels=[{"name": "Tayo"}, {"name": "Oyatt"}], resource_type="local", resources=[
                                                               "/workspaces/semi-automated-labeling/apps/streamlit/test_dataset/Bengal_197.jpg"])
                    # st.session_state.cvat_dataset.tasks_upload(
                    #     task_id=45,
                    #     fileformat="COCO 1.0",
                    #     filename=os.path.join(dataset_dir, "labels_new.json")
                    # )

                    st.success(
                        f"Success, dataset repository can be accessed at {repo_url}")
