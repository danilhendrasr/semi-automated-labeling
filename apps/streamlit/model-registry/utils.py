
from pathlib import Path
import shutil
import git
import os
import json
import requests

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

if __name__ == '__main__':

    import requests
    import json

    dict_ = {
        "tag_name":"v1.0",
        "target_commitish":"main",
        "name":"v1.0",
        "body":"Sample Release",
        "draft":False,
        "prerelease":False,
        "generate_release_notes":False
    }

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token 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",
        "Content-Type": "application/octet-stream"
    }

    # release_json = json.dumps(dict_)

    # release = requests.post(
    #     'https://api.github.com/repos/ruhyadi/sample-release/releases',
    #     headers=headers,
    #     data=release_json
    #     )

    # print(release)
    # print(release.json()['upload_url'])
    os.chdir(os.getcwd())
    assets_dict = {
        "name" : open('sample011.zip', 'rb')
    }

    assets = requests.post(
        'https://uploads.github.com/repos/ruhyadi/sample-release/releases/67446040/assets?name=sample011.zip',
        headers=headers,
        files=assets_dict
    )

    # print(release.json())
    print(assets)
    print(assets.json())
    print(os.getcwd())