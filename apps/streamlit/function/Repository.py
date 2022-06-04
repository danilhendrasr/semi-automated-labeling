
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
        tag: str, # or branch
        token: str,
    ):
        self.repo_url = repo_url
        self.tag = tag
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
            branch=self.tag
            )

        print(f'[INFO] Clone Repo in {self.repo_dir}')
        return repo
    

    
if __name__ == '__main__':

    repository = Repository(
        repo_url='https://github.com/ruhyadi/sample-release-1',
        tag='v1.0',
        token='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'
    )

    repository.init(is_private=True)
