import os
from pathlib import Path
from git import Repo
import shutil

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

if __name__ == "__main__":

    url = 'https://github.com/ruhyadi/light-repo'
    remote = '/home/intern-didir/Repository/labelling/apps/cvat'
    branch = 'main'
    token = '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'
    gpu = False

    deployment = DeployModel(url, remote, branch, token, gpu)

    # clone repository
    deployment.clone_repo()