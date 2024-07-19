import os
import re
import pyperclip

# 指定文件夹路径
folder_path = pyperclip.paste()  # 替换为你的文件夹路径

# 获取文件夹下所有文件夹的名称
subfiles = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
text = ','.join(subfiles)
# 使用正则表达式查找文件名中的数字，并去除可能存在的前导零
pattern = r'第0*(\d+)集'  # 匹配数字并去除前导零
matches = re.findall(pattern, text)
numbers = sorted(map(int, matches))
# 查找缺失的数字
missing_numbers = []
for i in range(min(numbers), max(numbers)):
    if i not in numbers:
        missing_numbers.append(i)

# 输出结果
if missing_numbers:
    print("缺失的数字:", missing_numbers)
else:
    print("没有缺失的数字")

