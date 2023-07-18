import os

def make_path(path, *paths):
    path = os.path.normpath(os.path.join(path, *paths))
    # dir path doesn't have ext. file path must have ext
    dir_path = os.path.split(path)[0] if os.path.splitext(path)[1] else path
    if dir_path and not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return path
