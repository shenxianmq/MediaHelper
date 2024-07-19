import os
import shutil

# 指定要遍历的根文件夹
root_folder = '/volume2/Media/custom/Emby'

# 指定视频文件后缀名
video_extensions = {'.mp4', '.avi', '.rmvb', '.wmv', '.mkv', '.ts'}

def is_video_file(filename):
    return any(filename.endswith(ext) for ext in video_extensions)

def delete_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not any(os.path.isdir(os.path.join(dir_path, sub_dir)) for sub_dir in os.listdir(dir_path)):
                if not any(is_video_file(file) for file in os.listdir(dir_path)):
                    print(f"已删除无视频文件夹: {dir_path}")
                    shutil.rmtree(dir_path)
if __name__ == '__main__':
    delete_empty_folders(root_folder)
