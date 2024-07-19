import os
import sys
import time
import shutil
import logging

# 配置日志
log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"empty_child_folder.log")
logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# 记录程序运行时间
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
logging.info(f"程序运行开始时间: {current_time}")


def empty_folder(folder_path):
    try:
        for i in os.listdir(folder_path):
            item_path = os.path.join(folder_path,i)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                    for dir in dirs:
                        dir_path = os.path.join(root,dir)
                        shutil.rmtree(dir_path)
                        logging.info(f'已删除文件夹: {dir_path}')
        logging.info(f'已清空文件夹: {folder_path}')
    except Exception as e:
        logging.error(e)

if __name__ == '__main__':
    # 获取要处理的文件夹列表
    folder_list = ["/volume2/Media/links/电影","/volume2/Media/links/电视剧","/volume2/Media/links/动漫"]

    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        user_input = sys.argv[1]  # 使用命令行参数作为用户输入
    else:
        # 获取用户输入，以逗号分隔的数字或 "all"
        user_input = input("请输入要处理的文件夹序号（以逗号分隔）或输入 'all' 处理所有文件夹: ")

    if user_input == "all":
        # 处理所有文件夹
        for folder in folder_list:
            empty_folder(folder)
    else:
        # 根据用户输入处理特定文件夹
        selected_folders = [int(num) - 1 for num in user_input.split(",")]
        for index in selected_folders:
            if 0 <= index < len(folder_list):
                folder = folder_list[index]
                empty_folder(folder)

    print("处理完成")
