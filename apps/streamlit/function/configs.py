"""Control Panel Configurations function"""

import os
import shutil
import fiftyone as fo

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
    """cleanup dump dir"""
    [fo.delete_dataset(name) for name in fo.list_datasets()]
    print("[INFO] All fiftyone datasets deleted.")
    shutil.rmtree(dump_dir)
    print("[INFO] Dump directory cleaned")
    os.makedirs(dump_dir)
    print("[INFO] Dump directory recreated")