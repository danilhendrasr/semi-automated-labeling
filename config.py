import os

port = {
    'cvat' : 8080,
    'flask' : 6001,
    'fiftyone' : 6002,
    'dash' : 6003,
    'streamlit' : 6004,
    'fiftyone-preview' : 6005
}

def get_url():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    url = s.getsockname()[0]
    s.close()
    return url

url = f'http://{get_url()}'

host = address = ip = '0.0.0.0'

max_upload_size = 1000    # Size in MB
auto_save_interval = 5    # interval in seconds

cache_folder = os.path.abspath('apps/dash/.cache')
os.makedirs(cache_folder, exist_ok=True)

