import os
from re import L
import subprocess
import time
import logging

# 配置日志
log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"hlink-sync-delete.log")
logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# 记录程序运行时间
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
logging.info(f"程序运行开始时间: {current_time}")

def log_error(message):
    logging.error(message)

def get_hard_links(file_path, start_folder):
    try:
        # 使用 stat 命令获取文件的 inode 号
        stat_result = subprocess.check_output(['stat', '-c', '%i', file_path])
        inode = int(stat_result.strip())

        # 使用 find 命令查找具有相同 inode 号的文件
        find_command = ['find', start_folder, '-inum', str(inode)]
        find_result = subprocess.check_output(find_command)
        hard_links = find_result.decode().strip().split('\n')
        find_command = ['find', recycle_folder, '-inum', str(inode)]
        find_result = subprocess.check_output(find_command)
        hard_links_2 = find_result.decode().strip().split('\n')
        if hard_links_2:
            hard_links.extend(hard_links_2)
        hard_links = [item for item in hard_links if item != ""]
        return hard_links
    except subprocess.CalledProcessError:
        return []

def get_file_age(file_path):
    current_time = time.time()
    file_creation_time = os.path.getctime(file_path)
    # 计算文件的存活时间
    file_age = current_time - file_creation_time
    return file_age

def delete_files_with_single_hardlink(folder_path, index):
    global file_deleted,folder_deleted
    for root, _, files in os.walk(folder_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            file_age = get_file_age(file_path)
            try:
                # 获取文件的硬链接数
                num_hardlinks = os.stat(file_path).st_nlink
                if num_hardlinks == 2:
                    hard_links = get_hard_links(file_path, links_folder_list[index])
                    if any("#recycle" in item for item in hard_links) and file_age > file_life:
                        os.remove(file_path)
                        file_deleted += 1
                        logging.info(f'已删除文件: {file_path}')
                        for file in hard_links:
                            os.remove(file)
                            file_deleted += 1
                            logging.info(f'已删除文件: {file}')
                elif num_hardlinks == 1 and file_age > file_life:
                    # 如果文件的存活时间超过10分钟才删除
                    if file_age > file_life:
                        os.remove(file_path)
                        file_deleted += 1
                        logging.info(f'已删除文件: {file_path}')
            except Exception as e:
                log_error(f"文件{file_path}出现错误:{e}")
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):  # 文件夹为空
                # 检查文件夹是否在白名单中
                os.rmdir(dir_path)
                folder_deleted += 1
                logging.info(f'已发现空文件夹: {dir_path}')

if __name__ == "__main__":
    folder_list = ["/volume2/Media/download/电影", "/volume2/Media/download/电视剧", "/volume2/Media/download/动漫"]
    links_folder_list = ["/volume2/Media/links/电影", "/volume2/Media/links/电视剧", "/volume2/Media/links/动漫"]
    recycle_folder = "/volume2/Media/#recycle"
    file_life = 1
    file_deleted = 0
    folder_deleted = 0
    for i, folder_to_clean in enumerate(folder_list):
        delete_files_with_single_hardlink(folder_to_clean, i)
    logging.info(f'程序运行完成:共删除{file_deleted}个文件,{folder_deleted}个文件夹.')
