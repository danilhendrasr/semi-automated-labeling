""" Repository class """

from operator import contains
import sys
import os
import json
import shutil
from pathlib import Path
from pprint import pprint
from typing import TypedDict
import git
import requests

from function.dvc import DVC
# from dvc import DVC


class RemoteRepoOptions(TypedDict):
    """ Options for initializing remote repository """
    private: bool
    description: str


class Repository:
    """
    Class for git functions with python
    """

    def __init__(
        self,
        repo_url: str,
        ref: str,  # or branch
        token: str,
        init_remote: RemoteRepoOptions = None,
        dump_dir: str = os.getcwd(),
        with_dvc=False,
    ):
        self.ref = ref
        self.token = token
        self.successfuly_created = True

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

        if init_remote is not None and len(init_remote) > 0:
            self.with_dvc = with_dvc
            init_dict = {
                "name": self.repo_name,
                "description": init_remote["description"],
                "private": init_remote["private"],
                "auto_init": True,
                "gitignore_template": 'Python',
            }

            response = requests.post(
                url='https://api.github.com/user/repos',
                headers=self.headers,
                data=json.dumps(init_dict)
            )

            repo_dir = self.clone()
            self.dvc = DVC(repo_dir)
            if str(response) == '<Response [201]>':
                print(response)
                if self.with_dvc:
                    self.commit(
                        git_items=[".dvc", ".dvcignore"], message="init dvc")
                    self.push()

                print(
                    f'[INFO] Success initializing repo {self.username}/{self.repo_name}')
            elif "422" in str(response):
                print(
                    f'[INFO] Success initializing repo {self.username}/{self.repo_name}')
            else:
                self.successfuly_created = False

    def init(self, description, private=True):
        """ Initalize remote repo """

        pass

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
        return self.repo_dir

    def checkout(self, ref='main'):
        repo = git.Repo(self.repo_dir)
        repo.git.checkout(ref)

        print(f"[INFO] Checkout to {ref}")

    def push(self):
        repo = git.Repo(self.repo_dir)
        repo.remotes.origin.push()
        if self.with_dvc:
            self.dvc.push()

    def tag(self, tag: str, with_commit=True):
        """ create tag """
        repo = git.Repo(self.repo_dir)

        if with_commit:
            # commit all files
            try:
                repo.git.add(all=True)
                repo.git.commit('-m', f'Version {tag}')
                repo.remotes.origin.push()
            except Exception as error:
                print(error)
                sys.exit(1)

        # create tag
        try:
            tag = repo.create_tag(path=tag, message=f'Version {tag}')
            repo.remotes.origin.push(tag)
        except Exception as error:
            print(error)

        print(f'[INFO] Success create tag {tag}')

    def commit(self, message: str, git_items: list[str], dvc_items: list[str] = None):
        repo = git.Repo(self.repo_dir)
        if self.with_dvc and dvc_items is not None:
            for dvc_item in dvc_items:
                self.dvc.add(dvc_item)

        repo.git.add(git_items)
        repo.git.commit('-m', message)

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
            "target_commitish": "main",  # self.ref
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
        print(
            f'[INFO] Success release {tag} with release id {response.json()["id"]}')

    def delete_release(self, release_id: str):
        """ Delete release by release id """
        response = requests.delete(
            url=f'https://api.github.com/repos/{self.username}/{self.repo_name}/releases/{release_id}',
            headers=self.headers
        )

        print(response)
        print(f'[INFO] Success deleted release {release_id}')

    def create_release(self, title: str, desc: str, tag: str, branch: str = "main", with_commit: bool = True):
        """Create release"""
        if with_commit:
            repo = git.Repo(self.repo_dir)
            try:
                repo.git.add(all=True)
                repo.git.commit('-m', f'Version {tag}')
                repo.remotes.origin.push()
            except Exception as e:
                print(e)
                sys.exit(1)

        url = f"https://api.github.com/repos/{self.username}/{self.repo_name}/releases"
        payload = {
            "tag_name": tag,
            "target_commitish": branch,
            "name": title,
            "body": desc,
            "draft": False,
            "prerelease": False,
            "generate_release_notes": True,
        }

        response = requests.post(
            url=f'https://uploads.github.com/repos/{self.username}/{self.repo_name}/releases/{release_id}/assets?name={filename}',
            headers=self.headers,
            files=assets_dict
        )

    def upload_assets(self, assets, release_id):
        """Post assets to release"""
        for asset in assets:
            asset_path = os.path.join(os.getcwd(), asset)
            with ZipFile(f"{asset_path}.zip", "w") as zip_file:
                zip_file.write(asset)
            asset_path = f"{asset_path}.zip"
            filename = asset_path.split("/")[-1]
            url = (
                f"https://uploads.github.com/repos/{self.username}/{self.repo_name}/releases/"
                + str(release_id)
                + f"/assets?name={filename}"
            )
            print("[INFO] Uploading {}".format(filename))
            response = requests.post(
                url, files={"name": open(asset_path, "rb")}, headers=self.headers)
            pprint(response.json())

    def get_assets(self, tag: str = None):
        """Get release assets by tag name"""
        tag = self.ref if tag == None else tag
        url = f'https://api.github.com/repos/{self.username}/{self.repo_name}/releases/tags/' + tag
        response = requests.get(url, headers=self.headers)
        return response.json()['assets']

    def download_assets(self, assets: list[dict]):
        """Download private assets from github release"""
        for asset in assets:
            url = f'https://api.github.com/repos/{self.username}/{self.repo_name}/releases/assets/' + str(
                asset['id'])
            response = requests.get(url, headers=self.headers)
            pprint(response.json())
            filename = asset['name']
            with open(os.path.join(self.repo_dir, filename), 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            del response
            with ZipFile(os.path.join(self.repo_dir, filename), 'r') as zip_file:
                zip_file.extractall(self.repo_dir)
            os.remove(os.path.join(self.repo_dir, filename))  # remove zip

            print(f"[INFO] Downloaded {filename}")

    def download_assets2(self, assets):
        """Download assets to repo directory"""
        for asset in assets:
            url = asset['browser_download_url']
            filename = asset['name']
            print('[INFO] Downloading {}'.format(filename))
            response = requests.get(url, headers=self.headers, stream=True)
            pprint(response)
            with open(os.path.join(self.repo_dir, filename), 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            del response

            with ZipFile(os.path.join(self.repo_dir, filename), 'r') as zip_file:
                zip_file.extractall(self.repo_dir)
            os.remove(os.path.join(self.repo_dir, filename))  # remove zip


if __name__ == '__main__':

    repository = Repository(
        repo_url='https://github.com/ruhyadi/dataset-registry-002',
        ref='v1.2',
        token='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',
        dump_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump"
    )

    # repository.clone(force=True)

    repository.checkout('main')
    repository.create_release(
        title='title', desc='desc', tag='v1.2.1', with_commit=True
    )

    # repository.checkout()

    # repository.list_tags()

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
