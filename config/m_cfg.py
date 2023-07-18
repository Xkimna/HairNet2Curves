import os

from tools.basic.m_config import Config
from tools.basic.m_file import make_path
from tools.basic.m_json import read_json


def get_or_create_cfg_path(workspace):
    return make_path(workspace, "config", "config.json")


def from_rel_path_cfg(workspace, path_cfg):
    for k, v in path_cfg.items():
        path_cfg[k] = os.path.normpath(os.path.join(workspace, path_cfg[k]))
    return path_cfg


def load_cfg(workspace):
    cfg = read_json(get_or_create_cfg_path(workspace))
    v = cfg.get("path", None)
    if v is not None:
        cfg["path"] = from_rel_path_cfg(workspace, v)
    return Config(cfg)
