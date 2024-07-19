import os
import time

def check_and_remove_files_with_one_hardlink(folder_path):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("无效的文件夹路径！")
        return

    for root, dirs, files in os.walk(folder_path,topdown=False):
        for file in files:
            if not file.endswith((".mkv", ".mp4", ".rmvb", ".avi")):
                continue
            file_path = os.path.join(root, file)
            hard_link_count = os.stat(file_path).st_nlink
            if hard_link_count == 1:  # 子文件夹中的文件硬链接数为1
                file_creation_time = os.path.getmtime(file_path)
                current_time = time.time()
                time_difference = current_time - file_creation_time
                hours_in_a_day = 24
                if time_difference > hours_in_a_day * 3600:  # 创建时间大于24小时
                    try:
                        # os.remove(file_path)  # 删除子文件夹中的文件
                        print("发现硬链接数为1且创建时间大于24小时的文件，已删除：", file_path)
                    except OSError as e:
                        print("删除文件时出错：", e)

    for root, dirs, files in os.walk(folder_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # 检查文件夹是否为空
                try:
                    os.rmdir(dir_path)  # 删除空文件夹
                    print("空文件夹已删除：", dir_path)
                except OSError as e:
                    print("删除文件夹时出错：", e)

if __name__ == '__main__':
    # 指定要检测的文件夹路径
    folder_path_list = ["/volume2/Media/download/电影", "/volume2/Media/download/电视剧", "/volume2/Media/download/动漫"]
    for folder_path in folder_path_list:
        check_and_remove_files_with_one_hardlink(folder_path)

