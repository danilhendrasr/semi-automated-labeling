"""
Utils for demo purpose
"""

import os
import json
import git
import shutil
import requests

from pathlib import Path
from git import Repo
from urllib.parse import quote

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

class DeployModel:
    def __init__(
        self, 
        url: str = 'https://github.com/username/repo_name', 
        remote: str = None,
        branch: str = 'main',
        token: str = None,
        gpu: bool = False,
        
    ):
        super().__init__()

        self.git_url = url
        self.remote_dir = Path(remote)
        self.branch = branch
        self.token = token
        self.gpu = gpu

        try:
            self.username = self.git_url.split('/')[3]
            self.repo_name = self.git_url.split('/')[4]
        except:
            self.username = 'username'
            self.repo_name = 'repo_name'
        self.save_path = str(Path(os.getcwd()) / 'serverless' / self.username / self.repo_name)
        if self.remote_dir is not None:
            self.save_path = str(self.remote_dir / 'serverless' / self.username / self.repo_name)
            
    def clone_repo(self):
        # make directory
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)
        else:
            shutil.rmtree(self.save_path)
            os.makedirs(self.save_path)

        # clone repository 
        if self.token is not None:
            private_url = f'https://{self.token}@github.com/{self.username}/{self.repo_name}.git'
            repo = Repo.clone_from(private_url, self.save_path, branch=self.branch)
        else:
            repo = Repo.clone_from(self.git_url, self.save_path, branch=self.branch)

        repo.git.checkout(self.branch)

        print(f'[INFO] Clone Repository to {self.save_path}')

    def deploy_model(self):
        ROOT = Path(os.getcwd())
        if self.remote_dir is not None:
            ROOT = self.remote_dir
        deploy_cpu = ROOT / 'serverless/deploy_cpu.sh'
        deploy_gpu = ROOT / 'serverless/deploy_gpu.sh'

        os.chdir(ROOT / 'serverless')
        if self.gpu is True:
            os.system(f'{deploy_gpu} {self.save_path}')
        else:
            os.system(f'{deploy_cpu} {self.save_path}')

class ModelRegistry():
    def __init__(self, git_url:str , token:str):
        
        self.git_url = git_url
        self.git_token = token

        self.username = self.git_url.split('/')[3]
        self.reponame = self.git_url.split('/')[4]
        self.repodir = Path(os.getcwd()) / self.username / self.reponame

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.git_token}",
            # "Content-Type": "image/png"
            "Content-Type": "application/octet-stream"
            # "Content-Type": "application/zip"
        }

    def clone_repo(self, force=True):

        if not os.path.isdir(self.repodir):
            os.makedirs(self.repodir)
        elif force:
            shutil.rmtree(self.repodir)
            os.makedirs(self.repodir)
        repo = git.Repo.clone_from(self.git_url, to_path=self.repodir)

    def create_release(self, title, tag, branch, desc):

        release_dict = {
            "tag_name":f"{tag}",
            "target_commitish":f"{branch}",
            "name":f"{title}",
            "body":f"{desc}",
            "draft":False,
            "prerelease":False,
            "generate_release_notes":False
        }

        release_json = json.dumps(release_dict)

        release_response = requests.post(
            f'https://api.github.com/repos/{self.username}/{self.reponame}/releases',
            headers=self.headers,
            data=release_json
            )

        print(release_response)
        print(release_response.json())

        return release_response.json()['upload_url']

    def upload_assets(self, filename, upload_url):

        upload_url = upload_url.split('{')[0]

        assets_dict = {
            "name" : open(filename, 'rb')
        }
        #'https://uploads.github.com/repos/ruhyadi/sample-release/releases/66158665/assets'
        response_assets = requests.post(
            f'{upload_url}?name={filename}',
            headers=self.headers,
            files=assets_dict
        )

        print(response_assets)
        print(response_assets.json())