""" Repository class """

from re import L
import sys
import os
import json
import shutil
from pathlib import Path
from pprint import pprint

import git
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
        dump_dir: str = os.getcwd()
    ):
        self.ref = ref
        self.token = token

        self.username = repo_url.split('/')[3]
        self.repo_name = repo_url.split('/')[4]
        self.repo_url = f'https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}.git'  
        # TODO: change cwd to tmp
        self.repo_dir = Path(dump_dir) / self.username / self.repo_name

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

        if str(response) == '<Response [201]>':
            print(response)
            print(f'[INFO] Success initialize {self.username}/{self.repo_name}')
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

    def tag(self, tag: str):
        """ create tag """
        repo = git.Repo(self.repo_dir)

        # commit all files
        try: 
            repo.git.add(all=True)
            repo.git.commit('-m', f'Version {tag}')
            repo.remotes.origin.push()
        except Exception as e:
            print(e)
            sys.exit(1)

        # create tag
        try:
            tag = repo.create_tag(path=tag, message=f'Version {tag}')
            repo.remotes.origin.push(tag)
        except Exception as e:
            print(e)

        print(f'[INFO] Success create tag {tag}')

    def list_release(self, get_tags: bool = False):
        """ List all release """
        response = requests.get(
            url=f'https://api.github.com/repos/{self.username}/{self.repo_name}/releases',
            headers=self.headers
        )
        print(response)
        
        if get_tags:
            return [tag['tag_name'] for tag in response.json()]
        else:
            return response

    def get_release(self, tag: str):
        """ Get release id by tag """
        response = requests.get(
            url=f'https://api.github.com/repos/{self.username}/{self.repo_name}/releases/tags/{tag}',
            headers=self.headers
        )

        print(response)
        print(f'[INFO] Get release id {response.json()["id"]}')

        return response.json()['id']

    def create_release(self, title: str, desc: str, tag: str, with_commit: bool = False):
        """ create release assets from tag (target) """

        if with_commit:
            repo = git.Repo(self.repo_dir)

            # commit all files
            try: 
                repo.git.add(all=True)
                repo.git.commit('-m', f'Version {tag}')
                repo.remotes.origin.push()
            except Exception as e:
                print(e)
                sys.exit(1)

        release_dict = {
            "tag_name": tag,
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

        print(response)
        print(f'[INFO] Success release {tag} with release id {response.json()["id"]}')
            
    def delete_release(self, release_id: str):
        """ Delete release by release id """
        response = requests.delete(
            url=f'https://api.github.com/repos/{self.username}/{self.repo_name}/releases/{release_id}',
            headers=self.headers
            )

        print(response)
        print(f'[INFO] Success deleted release {release_id}')

    def upload_assets(self, filename: str, release_id: str):
        """ upload assets to release assets """
        file_path = os.path.join(self.repo_dir, filename)
        assets_dict = {
            "name": open(file_path, 'rb')
        }

        response = requests.post(
            url=f'https://uploads.github.com/repos/{self.username}/{self.repo_name}/releases/{release_id}/assets?name={filename}',
            headers=self.headers,
            files=assets_dict
            )

        print(response)
        print(f'[INFO] Success upload {filename}')

if __name__ == '__main__':

    repository = Repository(
        repo_url='https://github.com/ruhyadi/sample-dataset-registry',
        ref='main',
        token='ghp_dKM1r4cfc1HWM7g97scGSatlgZWH0S3nfsZ'
    )

    repository.clone(force=True)

    repository.list_tags()

    # repository.init(is_private=True)
    # repository.clone(force=True)
    # repository.tag(tag='v1.2')
    # id = repository.release(
    #     title='v1.0',
    #     desc='Release v1.0',
    #     tag='v1.3'
    #     )
    # print(id) # 68624638
    # repository.upload_assets('newfile6', release_id='68624638')

    # tag = repository.list_release(get_tags=True)
    # print(tag)