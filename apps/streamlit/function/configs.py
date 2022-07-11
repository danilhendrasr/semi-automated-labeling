"""Control Panel Configurations function"""

import os
import shutil
import fiftyone as fo
import requests

def init_git_config(username, email):
    """initialize github configs"""
    # unset all variable
    os.system(f"git config --global --unset-all user.name")
    os.system(f"git config --global --unset-all user.email")
    # set username and email
    os.system(f"git config --global --replace-all user.name '{username}'")
    os.system(f"git config --global --replace-all user.email '{email}'")
    print("[INFO] Github configs initialized")

def cleanup_dump_dir(dump_dir):
    """Delete all fiftyone datasets."""
    requests.post('http://192.168.103.67:6001/fiftyone/delete/dataset')
    print("[INFO] All fiftyone datasets deleted.")
    """cleanup dump dir"""
    if os.path.exists(dump_dir):
        shutil.rmtree(dump_dir)
        print("[INFO] Dump dir cleaned")
        os.makedirs(dump_dir)
    else:
        os.makedirs(dump_dir)
        print("[INFO] Dump dir created")
