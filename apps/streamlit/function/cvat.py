""" cvat api class """

import json
import logging
import os
import shutil
from zipfile import ZipFile
import requests
from io import BytesIO
import mimetypes
from time import sleep
from PIL import Image

from typing import Tuple

from yaml import dump

log = logging.getLogger(__name__)

from .fiftyone51 import convert_format


class CVAT:
    def __init__(self, username: str, password: str, host: str, dump_dir: str):
        self.session = requests.Session()
        self.api = CVAT_API(host=host)
        self.login([username, password])
        self.dump_dir = dump_dir

    def tasks_list(self, use_json_output=True, **kwargs):
        """List all tasks in either basic or JSON format."""
        url = self.api.tasks
        response = self.session.get(url)
        response.raise_for_status()
        output = []
        page = 1
        json_data_list = []
        while True:
            response_json = response.json()
            output += response_json["results"]
            for r in response_json["results"]:
                if use_json_output:
                    json_data_list.append(r)
                else:
                    log.info("{id},{name},{status}".format(**r))
            if not response_json["next"]:
                log.info(json.dumps(json_data_list, indent=4))
                return output
            page += 1
            url = self.api.tasks_page(page)
            response = self.session.get(url)
            response.raise_for_status()

        return output

    def get_dataset_name(self, task_id):
        """Get dataset name by task id"""
        output = self.tasks_list(use_json_output=True)
        dataset_name = [data["name"] for data in output if data["id"] == task_id]

        return dataset_name.replace(" ", "_").lower()

    def tasks_data(self, task_id, resource_type, resources, **kwargs):
        """Add local, remote, or shared files to an existing task."""
        url = self.api.tasks_id_data(task_id)
        data = {}
        files = None
        if resource_type == "local":
            files = {
                "client_files[{}]".format(i): open(f, "rb")
                for i, f in enumerate(resources)
            }
        elif resource_type == "remote":
            data = {"remote_files[{}]".format(i): f for i, f in enumerate(resources)}
        elif resource_type == "share":
            data = {"server_files[{}]".format(i): f for i, f in enumerate(resources)}
        data["image_quality"] = 70

        ## capture additional kwargs
        for flag in [
            "chunk_size",
            "copy_data",
            "image_quality",
            "sorting_method",
            "start_frame",
            "stop_frame",
            "use_cache",
            "use_zip_chunks",
        ]:
            if kwargs.get(flag) is not None:
                data[flag] = kwargs.get(flag)
        if kwargs.get("frame_step") is not None:
            data["frame_filter"] = f"step={kwargs.get('frame_step')}"

        response = self.session.post(url, data=data, files=files)
        response.raise_for_status()

    def tasks_create(
        self,
        name,
        labels,
        resource_type,
        resources,
        annotation_path="",
        annotation_format="COCO 1.0",
        completion_verification_period=20,
        git_completion_verification_period=2,
        dataset_repository_url="",
        lfs=False,
        **kwargs,
    ):
        """Create a new task with the given name and labels JSON and
        add the files to it."""
        url = self.api.tasks
        labels = [] if kwargs.get("project_id") is not None else labels
        data = {"name": name, "labels": labels}

        for flag in ["bug_tracker", "overlap", "project_id", "segment_size"]:
            if kwargs.get(flag) is not None:
                data[flag] = kwargs.get(flag)

        response = self.session.post(url, json=data)
        response.raise_for_status()
        response_json = response.json()
        log.info("Created task ID: {id} NAME: {name}".format(**response_json))
        task_id = response_json["id"]
        self.tasks_data(task_id, resource_type, resources, **kwargs)

        if annotation_path != "":
            url = self.api.tasks_id_status(task_id)
            response = self.session.get(url)
            response_json = response.json()

            log.info("Awaiting data compression before uploading annotations...")
            while response_json["state"] != "Finished":
                sleep(completion_verification_period)
                response = self.session.get(url)
                response_json = response.json()
                logger_string = """Awaiting compression for task {}.
                            Status={}, Message={}""".format(
                    task_id, response_json["state"], response_json["message"]
                )
                log.info(logger_string)

            self.tasks_upload(task_id, annotation_format, annotation_path, **kwargs)
        if dataset_repository_url:
            response = self.session.post(
                self.api.git_create(task_id),
                json={"path": dataset_repository_url, "lfs": lfs, "tid": task_id},
            )
            response_json = response.json()
            rq_id = response_json["rq_id"]
            log.info(f"Create RQ ID: {rq_id}")
            check_url = self.api.git_check(rq_id)
            response = self.session.get(check_url)
            response_json = response.json()
            while response_json["status"] != "finished":
                log.info(
                    """Awaiting a dataset repository to be created for the task. Response status: {}""".format(
                        response_json["status"]
                    )
                )
                sleep(git_completion_verification_period)
                response = self.session.get(check_url)
                response_json = response.json()
                if (
                    response_json["status"] == "failed"
                    or response_json["status"] == "unknown"
                ):
                    log.error(
                        f"Dataset repository creation request for task {task_id} failed"
                        f'with status {response_json["status"]}.'
                    )
                    break

            log.info(
                f"Dataset repository creation completed with status: {response_json['status']}."
            )

    def tasks_delete(self, task_ids, **kwargs):
        """Delete a list of tasks, ignoring those which don't exist."""
        for task_id in task_ids:
            url = self.api.tasks_id(task_id)
            response = self.session.delete(url)
            try:
                response.raise_for_status()
                log.info("Task ID {} deleted".format(task_id))
            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    log.info("Task ID {} not found".format(task_id))
                else:
                    raise e

    def tasks_frame(self, task_id, frame_ids, outdir="", quality="original", **kwargs):
        """Download the requested frame numbers for a task and save images as
        task_<ID>_frame_<FRAME>.jpg."""
        for frame_id in frame_ids:
            url = self.api.tasks_id_frame_id(task_id, frame_id, quality)
            response = self.session.get(url)
            response.raise_for_status()
            im = Image.open(BytesIO(response.content))
            mime_type = im.get_format_mimetype() or "image/jpg"
            im_ext = mimetypes.guess_extension(mime_type)
            # FIXME It is better to use meta information from the server
            # to determine the extension
            # replace '.jpe' or '.jpeg' with a more used '.jpg'
            if im_ext in (".jpe", ".jpeg", None):
                im_ext = ".jpg"

            outfile = "task_{}_frame_{:06d}{}".format(task_id, frame_id, im_ext)
            im.save(os.path.join(outdir, outfile))

    def tasks_dump_annotations(
        self, task_id, fileformat, filename=None, extract=False, remove_zip=False, **kwargs
    ):
        """Download annotations for a task in the specified format
        (e.g. 'YOLO ZIP 1.0')."""
        url = self.api.tasks_id(task_id)
        response = self.session.get(url)
        response.raise_for_status()
        response_json = response.json()

        if filename is None:
            filename = 'dataset.zip'

        url = self.api.tasks_id_annotations_filename(
            task_id, filename, fileformat
        )
        while True:
            response = self.session.get(url)
            response.raise_for_status()
            log.info("STATUS {}".format(response.status_code))
            if response.status_code == 201:
                break

        response = self.session.get(url + "&action=download")
        response.raise_for_status()

        dataset_name = os.path.join(self.dump_dir, filename)
        dataset_dir = os.path.join(self.dump_dir, filename.split(".")[0])
        # download annotations (.zip)
        with open(filename, "wb") as fp:
            fp.write(response.content)

        if extract:
            with ZipFile(filename, "r") as zip:
                try:
                    os.makedirs(dataset_dir)
                except:
                    shutil.rmtree(dataset_dir)
                zip.extractall(dataset_dir)

        if remove_zip:
            os.remove(dataset_name)

    def tasks_dump(
        self, task_id, fileformat="COCO 1.0", filename='dataset.zip', extract=False, remove_zip=False, to_fiftyone=False, **kwargs
    ):
        """Download data & annotations for a task in the specified format
        (e.g. 'YOLO ZIP 1.0')."""
        url = self.api.tasks_id(task_id)
        response = self.session.get(url)
        response.raise_for_status()

        url = self.api.tasks_id_dataset(task_id, filename, fileformat)
        if to_fiftyone:
            url = self.api.tasks_id_dataset(task_id, filename, "COCO 1.0")

        while True:
            response = self.session.get(url)
            response.raise_for_status()
            log.info("STATUS {}".format(response.status_code))
            if response.status_code == 201:
                break

        url = "".join((url.split("?")[0], "?action=download&", url.split("?")[-1]))
        response = self.session.get(url)
        response.raise_for_status()

        dataset_name = os.path.join(self.dump_dir, filename)
        dataset_dir = os.path.join(self.dump_dir, filename.split(".")[0])
        # download dataset (.zip)
        with open(dataset_name, "wb") as fp:
            fp.write(response.content)

        if extract:
            with ZipFile(dataset_name, "r") as zip:
                try:
                    os.makedirs(dataset_dir)
                except:
                    shutil.rmtree(dataset_dir)
                zip.extractall(dataset_dir)
        
        if remove_zip:
            os.remove(dataset_name)

        if to_fiftyone:
            convert_format(dataset_dir, format=fileformat)

    def tasks_upload(self, task_id, fileformat, filename, **kwargs):
        """Upload annotations for a task in the specified format
        (e.g. 'YOLO ZIP 1.0')."""
        url = self.api.tasks_id_annotations_format(task_id, fileformat)
        while True:
            response = self.session.put(
                url, files={"annotation_file": open(filename, "rb")}
            )
            response.raise_for_status()
            if response.status_code == 201:
                break

        logger_string = "Upload job for Task ID {} ".format(
            task_id
        ) + "with annotation file {} finished".format(filename)
        log.info(logger_string)

    def tasks_export(self, task_id, filename, export_verification_period=3, **kwargs):
        """Export and download a whole task"""
        export_url = self.api.tasks_id(task_id) + "/backup"

        while True:
            response = self.session.get(export_url)
            response.raise_for_status()
            log.info("STATUS {}".format(response.status_code))
            if response.status_code == 201:
                break
            sleep(export_verification_period)

        response = self.session.get(export_url + "?action=download")
        response.raise_for_status()

        with open(filename, "wb") as fp:
            fp.write(response.content)
        logger_string = "Task {} has been exported sucessfully. ".format(
            task_id
        ) + "to {}".format(os.path.abspath(filename))
        log.info(logger_string)

    def tasks_import(self, filename, import_verification_period=3, **kwargs):
        """Import a task"""
        url = self.api.tasks + "/backup"
        with open(filename, "rb") as input_file:
            response = self.session.post(url, files={"task_file": input_file})
        response.raise_for_status()
        response_json = response.json()
        rq_id = response_json["rq_id"]
        while True:
            sleep(import_verification_period)
            response = self.session.post(url, data={"rq_id": rq_id})
            response.raise_for_status()
            if response.status_code == 201:
                break

        task_id = response.json()["id"]
        logger_string = "Task has been imported sucessfully. Task ID: {}".format(
            task_id
        )
        log.info(logger_string)

    def login(self, credentials):
        url = self.api.login
        auth = {"username": credentials[0], "password": credentials[1]}
        response = self.session.post(url, auth)
        response.raise_for_status()
        if "csrftoken" in response.cookies:
            self.session.headers["X-CSRFToken"] = response.cookies["csrftoken"]


class CVAT_API:
    def __init__(self, host, https=False):
        if host.startswith("https://"):
            https = True
        if host.startswith("http://") or host.startswith("https://"):
            host = host.replace("http://", "")
            host = host.replace("https://", "")
        scheme = "https" if https else "http"
        self.base = f"{scheme}://{host}/api/"
        self.git = f"{scheme}://{host}/git/repository/"

    @property
    def tasks(self):
        return self.base + "tasks"

    def tasks_page(self, page_id):
        return self.tasks + "?page={}".format(page_id)

    def tasks_id(self, task_id):
        return self.tasks + "/{}".format(task_id)

    def tasks_id_data(self, task_id):
        return self.tasks_id(task_id) + "/data"

    def tasks_id_data_update(self, task_id, file_id):
        return self.tasks_id(task_id) + "/data" + "/{}".format(file_id)

    def tasks_id_dataset(self, task_id, name, fileformat):
        # format fixed to COCO 1.0
        return self.tasks_id(task_id) + "/dataset?filename{}&format={}".format(
            name, fileformat
        )

    def tasks_id_frame_id(self, task_id, frame_id, quality):
        return self.tasks_id(task_id) + "/data?type=frame&number={}&quality={}".format(
            frame_id, quality
        )

    def tasks_id_status(self, task_id):
        return self.tasks_id(task_id) + "/status"

    def tasks_id_annotations_format(self, task_id, fileformat):
        return self.tasks_id(task_id) + "/annotations?format={}".format(fileformat)

    def tasks_id_annotations_filename(self, task_id, name, fileformat):
        return self.tasks_id(task_id) + "/annotations?format={}&filename={}".format(
            fileformat, name
        )

    def git_create(self, task_id):
        return self.git + f"create/{task_id}"

    def git_check(self, rq_id):
        return self.git + f"check/{rq_id}"

    @property
    def login(self):
        return self.base + "auth/login"


def deploy_model(repo_dir: str, serverless_dir: str, mode: str = "cpu"):
    deploy_cpu = os.path.join(serverless_dir, "deploy_cpu.sh")
    deploy_gpu = os.path.join(serverless_dir, "deploy_cpu.sh")

    os.chdir(serverless_dir)
    if mode == "gpu":
        os.system(f"{deploy_gpu} {repo_dir}")
    else:
        os.system(f"{deploy_cpu} {repo_dir}")


if __name__ == "__main__":

    from pprintpp import pprint

    cvat = CVAT(
        username="superadmin",
        password="KECILSEMUA",
        host="http://192.168.103.67:8080",
        dump_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump",
    )

    # cvat.tasks_upload(
    #     task_id=41,
    #     fileformat="COCO 1.0",
    #     filename="/home/intern-didir/Repository/labelling/apps/streamlit/41/labels.json",
    # )

    cvat.tasks_dump(
        task_id=39, 
        fileformat='YOLO 1.1', 
        filename='sample.zip',
        extract=True,
        remove_zip=True)

    # tasks_list = cvat.tasks_list()

    # pprint(tasks_list)
