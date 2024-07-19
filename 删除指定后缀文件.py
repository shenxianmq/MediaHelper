import os

working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)

num = 0

# 要删除文件的文件夹路径
dir_path = input("请输入文件夹路径")

# 要删除的文件后缀


for root, dirs, files in os.walk(dir_path):
    for file in files:
        if file.endswith(file_ext):
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                num += 1
                print(f"File deleted::: {file} total => {num}")
            except:
                pass
