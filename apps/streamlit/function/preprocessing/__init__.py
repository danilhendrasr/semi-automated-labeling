from . import process

import os
from PIL import Image

def inputs(name, function_key):
    if name == 'grayscale': return process.grayscale.inputs(function_key)
    if name == 'resize': return process.resize.inputs(function_key)
    if name == 'scale': return process.scale.inputs(function_key)

def preprocess(source, target, preprocess_list):
    os.makedirs(target, exist_ok=True)
    for path in os.listdir(source): Image.open(os.path.join(source, path)).save(os.path.join(target, path))
    for p in preprocess_list:
        if p['name'] == 'grayscale': process.grayscale.process(target, p['params'])
        if p['name'] == 'resize': process.resize.process(target, p['params'])
        if p['name'] == 'scale': process.scale.process(target, p['params'])