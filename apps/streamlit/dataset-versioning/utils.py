"""
Dataset versioning with DVC
Proof of Concept with Streamlit
Contributor: Didi Ruhyadi (@ruhyadi)
"""

from pathlib import Path
from git import Repo
import os
from urllib.parse import quote
import requests
import shutil

class DatasetVersioning:
    def __init__(
        self,
        dataset_type: str,
        repo: str, 
        dataset_version: str,
        filename: str,
        ids: str,
        annot_type: str,
        output_dir: str = None,
        username: str = 'superadmin',
        password: str = 'KECILSEMUA',
    ):
        self.dataset_type = str(dataset_type).lower()
        self.git_url = repo
        self.dataset_version = dataset_version
        self.filename = filename
        self.ids = ids
        self.annot_type = quote(annot_type)

        self.cvat_username = username
        self.cvat_password = password

        self.username = self.git_url.split('/')[3]
        self.repo_name = self.git_url.split('/')[4]

        self.output_dir = Path(os.getcwd()) / self.username / self.repo_name
        if output_dir is not None:
            self.output_dir = Path(output_dir) / self.username / self.repo_name

    def clone_repo(self, branch:str = 'main', token: str = None):
        # clone repository 
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
            if token is not None:
                private_url = f'https://{token}@github.com/{self.username}/{self.repo_name}.git'
                repo = Repo.clone_from(private_url, self.output_dir, branch=branch)
            else:
                repo = Repo.clone_from(self.git_url, self.output_dir, branch=branch)
        else:
            print('[INFO] Directory already exist')

    def download_dataset(self):
        url = 'http://192.168.103.67:8080/api/v1/projects/1/dataset?format=YOLO%201.1&filename=sample.zip&action=download'
        # http://192.168.103.67:8080/api/v1/tasks/3/dataset?format=YOLO%201.1&filename=sample&action=download

        self.api_url = f'http://192.168.103.67:8080/api/v1/\
            {self.dataset_type}/\
            {self.ids}/\
            dataset?format={self.annot_type}&\
            filename={self.filename}&\
            action=download'

        # download file
        self.download_file(self.api_url, output=self.output_dir / self.filename)
        
    def download_file(self, url, output):
        with requests.get(
            url,
            auth=requests.auth.HTTPBasicAuth(self.cvat_username, self.cvat_password),
            stream=True
        ) as r:
            with open(output, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return output

    def push_to_remote(self):
        os.chdir(self.output_dir)
        os.system(f'dvc add {self.filename}')
        os.system(f'dvc push')
        
    def versioning_git(self, author:str = 'ruhyadi.dr@gmail.com'):
        # init repo
        repo = Repo(self.output_dir)

        # add changing file, includes: filename.dvc, .gitignore, etc
        repo.git.add(all=True)
        repo.git.commit('-m', f'version {self.dataset_version}', author=author)

        # versioning git
        tag = repo.create_tag(self.dataset_version, message=f'automatic version {self.dataset_version}')
        repo.remotes.origin.push(tag)

if __name__ == '__main__':
    # download dataset

    downloader = DatasetVersioning(
        'tasks',
        'https://github.com/ruhyadi/sample',
        'v1.0',
        'sample.zip',
        '3',
        'YOLO 1.1')

    downloader.download_dataset()