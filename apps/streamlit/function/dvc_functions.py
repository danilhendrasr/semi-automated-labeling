""" DvC Functions """

from ast import Str
import os
from typing import List
import streamlit as st


def init(repo_dir: str, force: bool = False):
    """init dvc"""
    os.chdir(repo_dir)

    if force:
        os.system(f"dvc init -f")
    else:
        os.system(f"dvc init")


def add(repo_dir: str, folders: List = None, auto_stage: bool = True):
    """
    add changes in data
    folders: dataset -> default
    """
    os.chdir(repo_dir)

    if auto_stage:
        os.system("dvc config core.autostage true")

    if folders == None:
        os.system(f"dvc add dataset")
        print(f"[INFO] Success add to dvc")
    else:
        for folder in folders:
            os.system(f"dvc add {folder}")
            print(f"[INFO] Success add {folder} to dvc")


def remote(repo_dir: str, endpoint: str, remotes: str, remote_name: str = None):
    """add remotes storage"""

    assert remotes in ["gdrive", "azure", "s3"], "Remote Storage Not Supported"

    if remote_name is None:
        remote_name = remotes

    os.chdir(repo_dir)
    if remotes == "gdrive":
        os.system(f"dvc remote add -d {remote_name} gdrive://{endpoint}")
    # TODO: add more remotes storages

    print(f"[INFO] Success add {remotes} remote storage")


def push(repo_dir: Str):
    """push data to remotes"""

    os.chdir(repo_dir)
    os.system("dvc push")

    print(f"[INFO] Success push")


if __name__ == "__main__":

    from repository import Repository

    dummy_dir = "/home/intern-didir/Repository/labelling/apps/streamlit/dump_versioning"

    repo = Repository(
        repo_url="https://github.com/ruhyadi/sample-dataset-registry",
        ref="main",
        token="ghp_dKM1r4cfc1HWM7g97scGSatlgZWH0S3nfsZ",
        dump_dir=dummy_dir,
    )

    # repo.clone()
    init(repo_dir=repo.repo_dir, force=True)
    add(repo_dir=repo.repo_dir, auto_stage=True)
    remote(
        repo_dir=repo.repo_dir,
        remote_name="gdrive_remotes",
        endpoint="1RWymQlVq0Mes8BH2WeHn7mKCllxHcK-d",
        remotes="gdrive",
    )
    repo.tag(tag="v1.0.2")
    push(repo_dir=repo.repo_dir)