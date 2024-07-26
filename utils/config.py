import yaml
from typing import Dict


def concat(loader, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(_) for _ in seq])

def read_text(loader, node):
    path = loader.construct_scalar(node)
    with open(path, "r") as f:
        text = f.read()
    return text

# register the tag handlers
yaml.SafeLoader.add_constructor(tag='!concat', constructor=concat)
yaml.SafeLoader.add_constructor(tag='!read_text', constructor=read_text)

with open("resources/config.yml", "r") as f:
    conf:Dict = yaml.safe_load(f)
