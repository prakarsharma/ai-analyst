import yaml
from typing import Dict


def concat(loader, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(_) for _ in seq])

yaml.SafeLoader.add_constructor(tag='!concat', constructor=concat) # register the tag handler

with open("resources/config.yml", "r") as f:
    conf:Dict = yaml.safe_load(f)
