import yaml

def load_config(file):
    with open(file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)
