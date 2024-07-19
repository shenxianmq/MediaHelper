import os
import re
import shutil
import traceback

tmdb_list = []

# 这个是基准电影库
base_dir = "/Users/shenxian/CloudNAS/CloudDrive2/115/看剧/影视合集/电影/4K Remux"
for root, dirs, files in os.walk(base_dir):
    for dir in dirs:
        if "tmdb" in dir:
            tmdbid = re.findall(r"tmdb.*?(\d+)", dir)
            tmdb_list.append(tmdbid[0])
num = 0

# # 这个是基准电影库
# base_dir = "/Users/shenxian/CloudNAS/CloudDrive2/115/abc"
# for root, dirs, files in os.walk(base_dir):
#     for dir in dirs:
#         if "tmdb" in dir:
#             tmdbid = re.findall(r"tmdb.*?(\d+)", dir)
#             tmdb_list.append(tmdbid[0])

# 这里面填你要查重的电影库
target_dir_list = [
    "/Users/shenxian/CloudNAS/CloudDrive2/115/abc",
]
for root_dir in target_dir_list:
    for root, dirs, files in os.walk(root_dir):
        for dir in dirs:
            if "tmdb" in dir:
                tmdbid = re.findall(r"tmdb.*?(\d+)", dir)
                if tmdbid[0] in tmdb_list:
                    num += 1
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path)
                        print(f"dir deleted::: {dir}")
                    except:
                        print(f"error::: {dir_path}")
                        print(traceback.format_exc())
print(num)
