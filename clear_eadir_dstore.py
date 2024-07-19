import os
import subprocess

def delete_eadir_and_dsstore(path):
    try:
        for root, dirs, files in os.walk(path, topdown=False):
            # 删除名为"@eaDir"的文件夹
            for dir_name in dirs[:]:
                if dir_name == "@eaDir":
                    dir_path = os.path.join(root, dir_name)
                    subprocess.run(['rm', '-rf', dir_path])
                    print(f"Deleted folder: {dir_path}")

            # 删除后缀为".DS_Store"的文件
            for file_name in files:
                if file_name.endswith(".DS_Store"):
                    file_path = os.path.join(root, file_name)
                    subprocess.run(['rm', file_path])
                    print(f"Deleted file: {file_path}")

        print("Deletion complete.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    folder_list = ["/volume2/Media","/volume1/CloudNAS/CloudDrive2/115/看剧"]
    for folder_path in folder_list:
        delete_eadir_and_dsstore(folder_path)
