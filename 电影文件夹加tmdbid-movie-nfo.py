import os
import re

working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)


def rename_folders(root_dir):
    # 遍历指定文件夹下的所有子文件夹
    for subdir, dirs, files in os.walk(root_dir, topdown=False):
        for folder in dirs:
            # 判断文件夹名称中是否包含tmdbid
            if "tmdbid" in folder and "(" in folder:
                continue  # 跳过包含tmdbid的文件夹
            folder_path = os.path.join(subdir, folder)
            nfo_file = [f for f in os.listdir(folder_path) if f.endswith(".nfo")]
            if nfo_file:
                nfo_file = nfo_file[0]
                nfo_file_path = os.path.join(folder_path, nfo_file)
                try:
                    with open(nfo_file_path, "r", encoding="utf-8") as f:
                        nfo_content = f.read()
                        # 使用正则表达式获取tmdbid
                except:
                    with open("error.txt", "a") as f:
                        f.write(f"{folder_path}\n")
                    continue
                match = re.search(
                    r'<uniqueid.*?type="tmdb".*?>(\d+)</uniqueid>', nfo_content
                )
                if match:
                    tmdbid = match.group(1)
                    new_folder_name = f"{folder} {{tmdb-{tmdbid}}}"
                    new_folder_name = (
                        new_folder_name.replace("(", " (")
                        .replace(")", ") ")
                        .replace("  ", " ")
                    )
                    new_folder_path = os.path.join(subdir, new_folder_name)
                    os.rename(folder_path, new_folder_path)
                    print(f"Renamed folder '{folder}' to '{new_folder_name}'")
                else:
                    with open(
                        "/Users/shenxian/Desktop/error.txt", "a", encoding="utf-8"
                    ) as f:
                        f.write(folder_path + "\n")
                    print(f"No uniqueid found in .nfo files in folder '{folder}'")
            else:
                print(f"No .nfo files found in folder '{folder}'")


# 指定要遍历的文件夹路径
root_directory = "/Users/shenxian/CloudNAS/CloudDrive2/115(Wen)/Shenxian/已完成电影"

# 调用函数进行文件夹重命名
rename_folders(root_directory)
