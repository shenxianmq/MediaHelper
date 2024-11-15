import os
from posixpath import basename
import subprocess
import sys

alass_path = r'\volume1\Shencode\subsync\alass'
def process_videos(search_directory):
    subtitle_ext_list = ['.srt', '.ass', '.zh.srt', '.zh.ass', 'chs.srt', '.chs.ass']
    total_processed = 0  # 用于跟踪处理的字幕数量

    for root, dirs, files in os.walk(search_directory):
        for video_file in files:
            if video_file.lower().endswith(('.avi', '.mkv', '.wmv', '.mp4', '.mpeg', '.m4v')):
                video_filepath = os.path.join(root, video_file)
                video_filename = os.path.splitext(video_file)[0]
                video_name = os.path.splitext(video_filepath)[0]
                subtitle_path_list = [f'{video_name}{i}' for i in subtitle_ext_list]
                for subtitle_path in subtitle_path_list:
                    if os.path.exists(subtitle_path):
                        print(f"开始同步字幕时间轴: {subtitle_path}")
                        file_name,ext = os.path.splitext(subtitle_path)
                        cmd = [alass_path, video_filepath,subtitle_path,f'{file_name}.new{ext}']
                        subprocess.call(cmd)
                        total_processed += 1
                        print(f"成功同步字幕时间轴: {subtitle_path}")
                        sys.exit()

    print(f"一共处理了 {total_processed} 个字幕。")

if __name__ == "__main__":
    search_directory = input('请输入要同步的目录')
    search_directory = rf'{search_directory}'
    process_videos(search_directory)
