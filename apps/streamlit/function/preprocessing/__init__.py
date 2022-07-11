from . import process

import os, shutil
from PIL import Image

def inputs(name, function_key):
    if name == 'Grayscale': return process.grayscale.inputs(function_key = '{function_key} grayscale')
    if name == 'Resize': return process.resize.inputs(function_key = '{function_key} resize')
    if name == 'Scale': return process.scale.inputs(function_key = '{function_key} scale')
    if name == 'Filter by size': return process.filter_size.inputs(function_key = '{function_key} filter size')

def preprocess(source, target, preprocess_list):
    assert source != target, f'source {source} and target {target} must not be same.'
    if os.path.exists(target): shutil.rmtree(target)
    os.makedirs(target)
    for path in os.listdir(source): Image.open(os.path.join(source, path)).save(os.path.join(target, path))
    for p in preprocess_list:
        if p['name'] == 'Grayscale': process.grayscale.process(target, p['params'])
        if p['name'] == 'Resize': process.resize.process(target, p['params'])
        if p['name'] == 'Scale': process.scale.process(target, p['params'])
        if p['name'] == 'Filter by size': process.filter_size.process(target, p['params'])