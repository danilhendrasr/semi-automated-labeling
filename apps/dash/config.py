import os

port = {
    'flask' : 7011,
    'fiftyone' : 7012,
    'dash' : 7013,
}

host = address = ip = '0.0.0.0'

url = 'http://192.168.103.67'

cache_folder = '.cache'
os.makedirs(cache_folder, exist_ok=True)

auto_save_interval = 5    # interval in seconds