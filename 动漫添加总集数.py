import os
import re
from clouddrive import *

folder_path = "/Volumes/dav/115/我的接收/日漫/银魂.2006"
mkv_list = []
nfo_list = []
ass_list = []
for root, _, files in os.walk(folder_path):
    for file in files:
        if "SubBackup" in root:
            continue
        if file.endswith("mkv"):
            file_path = os.path.join(root, file)
            mkv_list.append(file_path)
        elif file.endswith("nfo") and "第" in file:
            file_path = os.path.join(root, file)
            nfo_list.append(file_path)
        elif file.endswith("ass"):
            file_path = os.path.join(root, file)
            ass_list.append(file_path)

if mkv_list:
    mkv_list.sort(
        key=lambda x: int(
            int(re.findall("S0*(\d+)", x)[0]) * 1000
            + int(re.findall("第0*(\d+)集", x)[0])
        )
    )
if nfo_list:
    nfo_list.sort(
        key=lambda x: int(
            int(re.findall("S0*(\d+)", x)[0]) * 1000
            + int(re.findall("第0*(\d+)集", x)[0])
        )
    )
if ass_list:
    ass_list.sort(
        key=lambda x: int(
            int(re.findall("S0*(\d+)", x)[0]) * 1000
            + int(re.findall("第0*(\d+)集", x)[0])
        )
    )

from clouddrive import CloudDriveClient, CloudDriveFileSystem

client = CloudDriveClient("cd2地址", "账号", "密码")
fs = CloudDriveFileSystem(client)

for i, file_path in enumerate(mkv_list):
    file_path = file_path.replace("/Volumes/dav", "")
    new_file_path = file_path.replace("集", f"集({i+1})")
    fs.rename(file_path, new_file_path)
    print(new_file_path)

for i, file_path in enumerate(nfo_list):
    file_path = file_path.replace("/Volumes/dav", "")
    new_file_path = file_path.replace("集", f"集({i+1})")
    fs.rename(file_path, new_file_path)
    print(new_file_path)

for i, file_path in enumerate(ass_list):
    file_path = file_path.replace("/Volumes/dav", "")
    new_file_path = file_path.replace("集", f"集({i+1})")
    fs.rename(file_path, new_file_path)
    print(new_file_path)
