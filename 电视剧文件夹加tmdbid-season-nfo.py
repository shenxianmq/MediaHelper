import os
import re

working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)


def rename_folders(root_dir):
    # 遍历指定文件夹下的所有子文件夹
    for subdir, dirs, files in os.walk(root_dir, topdown=False):
        for file in files:
            if file == "tvshow.nfo":
                nfo_file_path = os.path.join(subdir, file)
                folder_path = os.path.dirname(nfo_file_path)
                folder_name = os.path.basename(folder_path)
                if "tmdbid" in folder_name:
                    continue
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
                try:
                    if match:
                        tmdbid = match.group(1)
                        new_folder_name = f"{folder_name} {{tmdbid={tmdbid}}}"
                        new_folder_name = (
                            new_folder_name.replace("(", " (")
                            .replace(")", ") ")
                            .replace("  ", " ")
                        )
                        new_folder_path = os.path.join(
                            os.path.dirname(folder_path), new_folder_name
                        )
                        os.rename(folder_path, new_folder_path)
                        # print(folder_path)
                        # print(new_folder_path)
                        print(f"Renamed folder '{folder_name}' to '{new_folder_name}'")
                    else:
                        with open(
                            "/Users/shenxian/Desktop/error.txt", "a", encoding="utf-8"
                        ) as f:
                            f.write(folder_path + "\n")
                        print(
                            f"No uniqueid found in .nfo files in folder '{folder_name}'"
                        )
                except:
                    with open(
                        "/Users/shenxian/Desktop/error.txt", "a", encoding="utf-8"
                    ) as f:
                        f.write(folder_path + "\n")


# 指定要遍历的文件夹路径
root_directory = "/Users/shenxian/CloudNAS/CloudDrive2/115/我的接收/日韩剧"

# 调用函数进行文件夹重命名
rename_folders(root_directory)
