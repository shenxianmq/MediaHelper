import os
import re
import pyperclip

#文件名中必须包括“第”集
#文件所在文件夹必须以Season 1的格式命名
def offset_vedio(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and '第' in f]

    if not files:
        if any('Season' in i for i in os.listdir(folder_path)):
            folder_list = [os.path.join(folder_path,f) for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f)) and 'Season' in f]
            for folder in folder_list:
                offset_vedio(folder)
            return
        else:
            print("没有找到包含'第'的文件名。")
            return

    # 提取所有文件名中的集数
    episode_numbers = [int(re.findall(r'第(\d+)集', file)[0]) for file in files]
        # 找到最小的集数
    min_episode_number = min(episode_numbers)

    # 计算偏移量，使最小集数变为1
    offset = 1 - min_episode_number
    season_num = ''
    if 'Season' in folder_path:
        season_num = int(re.findall('.*? (\d+)',folder_path)[0])
    for file in files:
        file_path = os.path.join(folder_path,file)
        num = re.findall('第(\d+)集',file)[0]
        now_season_num = re.findall('S0*(\d+)E',file)[0]
        if not season_num:
            season_num = now_season_num
        new_num = int(num) + offset
        new_filepath = file_path.replace(f'E{int(num):02d}',f'E{new_num:02d}').replace(f'第{num}集',f'第{new_num}集').replace(f'S{int(now_season_num):02d}E',f'S{int(season_num):02d}E')
        os.rename(file_path,new_filepath)
        print(f'已成功偏移集数{new_filepath}')

if __name__ == '__main__':
    folder_path = pyperclip.paste()
    offset_vedio(folder_path)