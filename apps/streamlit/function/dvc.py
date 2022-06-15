import os

from dotenv import load_dotenv

load_dotenv()
azure_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
azure_access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")


class DVC:
    """ DVC Utility Class """

    def __init__(self, path: str) -> None:
        self.repo_dir = path
        if not os.path.isdir(f"{self.repo_dir}/.dvc"):
            os.chdir(self.repo_dir)
            os.system("dvc init && dvc remote add -d main azure://dataset-upload")
            self.setup_remote_credentials()

    def setup_remote_credentials(self):
        """ Set up local dvc credentials needed to interact with remote storage """
        os.chdir(self.repo_dir)
        os.system(f"dvc remote modify --local main account_name '{azure_account_name}' \
                && dvc remote modify --local main account_key '{azure_access_key}' ")

    def pull(self):
        """ Pull dataset """
        os.chdir(self.repo_dir)
        os.system("dvc pull")

    def add(self, item: str):
        """ Add item to DVC tracking """
        os.chdir(self.repo_dir)
        os.system(f"dvc add {item}")

    def push(self):
        """ Push dataset to remote storage """
        os.chdir(self.repo_dir)
        os.system("dvc push")
