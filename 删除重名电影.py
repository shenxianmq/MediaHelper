import os
import re
import shutil


def remove_duplicate_movies(base_dir, dest_dir):
    movie_list = get_movie_list(base_dir)
    for root, dirs, files in os.walk(dest_dir):
        for dir_name in dirs:
            if "(" not in dir_name:
                continue
            if any(movie_name in dir_name for movie_name in movie_list):
                dir_path = os.path.join(root, dir_name)
                print(f"发现重复的电影: {dir_path}")
                try:
                    if os.path.exists(dir_path):
                        shutil.rmtree(dir_path)
                except:
                    pass
                with open(
                    "/Users/shenxian/Desktop/res.txt", "a", encoding="utf-8"
                ) as f:
                    f.write(f"{dir_path}\n")


def get_movie_list(dir_path):
    movie_list = []
    num = 0
    for root, dirs, files in os.walk(dir_path):
        for dir_name in dirs:
            if "(" not in dir_name:
                continue
            movie_name = re.findall(r"(.*)?\(", dir_name)
            if movie_name:
                num += 1
                print(movie_name[0], num)
                movie_list.append(movie_name[0].strip())
    return movie_list


# 调用代码
remove_duplicate_movies(
    "/Users/shenxian/CloudNAS/CloudDrive2/115/看剧/FRDS电影mUHD大包",
    "/Users/shenxian/CloudNAS/CloudDrive2/115/我的接收/已刮削",
)
