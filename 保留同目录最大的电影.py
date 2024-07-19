import os
import shutil


def remove_metadata(filepath):
    dir_path = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    for ext in [
        ".nfo",
        "-clearlogo.png",
        "-fanart.jpg",
        "-landscape.jpg",
        "-poster.jpg",
    ]:
        file = os.path.join(dir_path, filename + ext)
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"metadata file deleted: {file}")
            except:
                pass


def find_largest_mkv(directory):
    """
    遍历指定目录下的一级子目录,找到每个子目录中最大的mkv文件并删除其他的。
    """
    for subdir in os.listdir(directory):
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            mkv_files = [f for f in os.listdir(subdir_path) if f.endswith(".mkv")]
            if len(mkv_files) > 1:
                largest_mkv = max(
                    mkv_files,
                    key=lambda x: os.path.getsize(os.path.join(subdir_path, x)),
                )
                for mkv in mkv_files:
                    if mkv != largest_mkv:
                        os.remove(os.path.join(subdir_path, mkv))
                        remove_metadata(os.path.join(subdir_path, mkv))
                        print(f"已删除 {os.path.join(subdir_path, mkv)}")
                print(f"找到最大的mkv文件: {os.path.join(subdir_path, largest_mkv)}")


# 使用示例
dir_list = [
    "/Users/shenxian/CloudNAS/CloudDrive2/115/看剧/影视合集/电影/Remux/欧美电影",
    "/Users/shenxian/CloudNAS/CloudDrive2/115/看剧/影视合集/电影/Remux/华语电影",
    "/Users/shenxian/CloudNAS/CloudDrive2/115/看剧/影视合集/电影/Remux/日韩电影",
    "/Users/shenxian/CloudNAS/CloudDrive2/115/看剧/影视合集/电影/Remux/动画电影",
]
if __name__ == "__main__":
    for source_dir in dir_list:
        find_largest_mkv(source_dir)
