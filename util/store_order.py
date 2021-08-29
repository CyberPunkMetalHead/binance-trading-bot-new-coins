import json
from typing import Dict


def store_order(file: str, order: Dict):
    """
        Save order into local json file
        """
    with open(file, 'w') as f:
        json.dump(order, f, indent=4)


def load_order(file: str):
    """
    Update Json file
    """
    with open(file, "r+") as f:
        return json.load(f)
