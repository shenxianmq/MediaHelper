import os
import re
from clouddrive import CloudDriveClient, CloudDriveFileSystem
client = CloudDriveClient("http://shenxianmq.x3322.net:19798", "31564266@qq.com", "sjmq123456")
fs = CloudDriveFileSystem(client)

for root, dirs, files in os.walk('/Volumes/dav/115/看剧/links'):
    for dir in dirs:
        if 'Season' not in dir and '.' in dir:
            dir_path = os.path.join(root,dir)
            new_dir_path = re.sub(r'\.(\d+)', r'(\1)',dir_path)
            print(new_dir_path)