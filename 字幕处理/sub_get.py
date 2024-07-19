import os
import subprocess
import threading
import shenmail
import sys

class SubtitleExtractor:
    def __init__(self, folder_path, sub_num, sub_ext):
        self.folder_path = folder_path
        self.sub_num = int(sub_num) - 1
        self.sub_ext = sub_ext

    def extract_subtitles(self):
        count = 0
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.mkv') or file.endswith('.mp4'):
                    mkv_path = os.path.join(root, file)

                    output_subfile = f'{os.path.splitext(mkv_path)[0]}.chs.{self.sub_ext}'
                    if os.path.exists(output_subfile):
                        os.remove(output_subfile)
                    cmd = f'ffmpeg -i "{mkv_path}" -map 0:s:{self.sub_num} "{output_subfile}"'
                    os.system(cmd)
                    count += 1
                    print(f"成功提取字幕: {file}")

        print(f"提取完成，共提取 {count} 个字幕")
        shenmail.send_bark(f'字幕提取成功\n{self.folder_path}\n成功提取{count}个字幕')

def main():
    if len(sys.argv) != 4:
        print("请提供文件夹路径、字幕流编号和字幕格式作为参数。")
        print("示例: python script.py '/path/to/folder' '1' 'srt'")
        sys.exit(1)

    folder_path = sys.argv[1]
    sub_num = sys.argv[2]
    sub_ext = sys.argv[3]

    extractor = SubtitleExtractor(folder_path, sub_num, sub_ext)
    extractor.extract_subtitles()

if __name__ == "__main__":
    main()