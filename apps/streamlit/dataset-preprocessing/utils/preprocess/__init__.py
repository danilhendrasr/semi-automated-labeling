__all__ = ['grayscale', 'resize', 'scale']
from . import *

from .config import config

def get_names():
    return list(config.keys())

def get_columns(name):
    columns = []
    params = config[name]
    for param in params:
        columns.append(param['column'])
    return columns

def get_labels(name):
    labels = []
    params = config[name]
    for param in params:
        labels.append(param['label'])
    return labels

def preprocess(preprocess_list):
    for p in preprocess_list:
        if p['name'] == 'grayscale': grayscale.process(p['params'])
        if p['name'] == 'resize': resize.process(p['params'])
        if p['name'] == 'scale': scale.process(p['params'])