from . import process

def inputs(name, key):
    if name == 'grayscale': return process.grayscale.inputs(key)
    if name == 'resize': return process.resize.inputs(key)
    if name == 'scale': return process.scale.inputs(key)

def preprocess(path, preprocess_list):
    for p in preprocess_list:
        if p['name'] == 'grayscale': process.grayscale.process(path, p['params'])
        if p['name'] == 'resize': process.resize.process(path, p['params'])
        if p['name'] == 'scale': process.scale.process(path, p['params'])