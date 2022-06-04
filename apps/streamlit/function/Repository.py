
from platform import release
from pprint import pprint
import git
import os
import json
import shutil
from pathlib import Path
import requests

class Repository:
    """
    Class for git functions with python
    """
    def __init__(
        self,
        repo_url: str,
        ref: str, # or branch
        token: str,
    ):
        self.repo_url = repo_url
        self.ref = ref
        self.token = token

        self.username = self.repo_url.split('/')[3]
        self.repo_name = self.repo_url.split('/')[4]
        # TODO: change cwd to tmp
        self.repo_dir = Path(os.getcwd()) / self.username / self.repo_name

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
            "Content-Type": "application/octet-stream"
        }

    def init(self, is_private: bool = False):
        """ initialize repo with github rest api """
        init_dict = {
            "name": self.repo_name,
            "description": "automatic init repo",
            "private": is_private,
            "auto_init": True,
            "gitignore_template": 'Python',
        }

        response = requests.post(
            url='https://api.github.com/user/repos',
            headers=self.headers,
            data=json.dumps(init_dict)
        )

        if response == '<Response [201]>':
            print(response)
            print(f'[INFO] Success initialize {self.repo_url}')
        else:
            print(response)
            pprint(response.json())
    
    def clone(self, force: bool = True):
        """ Clone from repository url """
        if not os.path.exists(self.repo_dir):
            os.makedirs(self.repo_dir)
        elif force:
            shutil.rmtree(self.repo_dir)
            os.makedirs(self.repo_dir)
            
        repo = git.Repo.clone_from(
            url=self.repo_url,
            to_path=self.repo_dir,
            branch=self.ref
            )

        print(f'[INFO] Clone Repo in {self.repo_dir}')
        return repo
    
    def release(self, title: str, desc: str, target: str):
        """ create release assets from tag (target) """
        release_dict = {
            "tag_name": target,
            "target_commitish": self.ref,
            "name": title,
            "body": desc,
            "draft": False,
            "prerelease": False,
            "generate_release_notes": True
        }

        response = requests.post(
            url=f'https://api.github.com/repos/{self.username}/{self.repo_name}/releases',
            headers=self.headers,
            data=json.dumps(release_dict)
            )

        if response == '<Response [201]>':
            print(response)
            print(f'[INFO] Success release {target}')
        else:
            print(response)
            pprint(response.json())

        # release id
        return response.json()['id']

    def upload_assets(self, filename, release_id):
        """ upload assets to release assets """
        assets_dict = {
            "name": open(filename, 'rb')
        }

        response = requests.post(
            url=f'https://uploads.github.com/repos/{self.username}/{self.repo_name}/releases/{release_id}/assets?name={filename}',
            headers=self.headers,
            files=assets_dict
            )

        if response == '<Response [201]>':
            print(response)
            print(f'[INFO] Success upload {filename}')
        else:
            print(response)
            pprint(response.json())


if __name__ == '__main__':

    repository = Repository(
        repo_url='https://github.com/ruhyadi/sample-release-1',
        ref='v1.0',
        token='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'
    )

    repository.init(is_private=True)