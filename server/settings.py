import pathlib

import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
config_path = BASE_DIR / "config" / "dev_example.yaml"
# config_path = BASE_DIR / "config" / "dev_example.yaml"


def get_config(path):
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return cfg


config = get_config(config_path)
