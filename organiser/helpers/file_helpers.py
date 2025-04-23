import os
import shutil
import logging


def create_dictionary_if_not_exist(path_to_create):
    if not os.path.exists(path_to_create):
        os.mkdir(path_to_create)


def copy_if_exists(orig_path, new_path):
    if os.path.exists(orig_path):
        shutil.copy2(orig_path, new_path)
    else:
        logging.warning(f"Path {orig_path} does not exist!")


def copy_folder_if_exists(orig_path, new_path, ignore_list=None):
    if ignore_list is None:
        ignore_list = []
    if os.path.exists(orig_path):
        ignore_func = shutil.ignore_patterns(*ignore_list)
        shutil.copytree(orig_path, new_path, ignore=ignore_func)
    else:
        logging.warning(f"Path {orig_path} does not exist!")
