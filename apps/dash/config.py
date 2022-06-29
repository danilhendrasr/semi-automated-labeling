import os

port = {
    'flask' : 7021,
    'fiftyone' : 7022,
    'dash' : 7023,
}

host = address = ip = '0.0.0.0'

url = 'http://192.168.103.67'

cache_folder = '.cache'
os.makedirs(cache_folder, exist_ok=True)

auto_save_interval = 5    # interval in seconds