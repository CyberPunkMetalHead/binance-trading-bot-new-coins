import yaml
from typing import Dict


def load_config(file: str) -> Dict:
    with open(file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)
