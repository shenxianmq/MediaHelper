import os
from posixpath import dirname, realpath, relpath
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import configparser
import threading
import codecs
import re
import shutil
import platform

current_os = platform.system()
root_dir = os.path.dirname(os.path.abspath(__file__))
alass_path = os.path.join(root_dir,'alass','alass.bat')
alass_path_win = r"C:\alass\alass.bat"
alass_path_mac = r"/Users/shenxian/alass"
line_count = 150

def get_desktop_path():
    system = platform.system()
    if system == "Windows":
        # Windows 桌面路径通常在用户文件夹下
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    elif system == "Darwin":
        # macOS 桌面路径也在用户文件夹下
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    elif system == "Linux":
        # Linux 桌面路径可以在用户文件夹下，也可能在 ~/桌面 目录下
        desktop_path = os.path.join(os.path.expanduser("~"), "桌面")  # Linux 桌面路径示例
    else:
        # 其他操作系统的处理，或者您可以定义一个默认路径
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    return desktop_path

def detect_and_convert_encoding(input_file):
    encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]

    for enc in encodings:
        try:
            with codecs.open(input_file, mode="r", encoding=enc,errors="ignore") as fd:
                content = fd.read()

            # 如果文件内容不为空，则表示找到了正确的编码
            if content:
                with codecs.open(input_file, 'w', 'utf-8') as fd:
                    fd.write(content)
                return True

        except Exception as e:
            continue
    # 如果所有编码都无法正常读取，则返回 False
    return False


def detect_and_convert_encoding(input_file):
    encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]

    for enc in encodings:
        try:
            with codecs.open(input_file, mode="r", encoding=enc,errors="ignore") as fd:
                content = fd.read()

            # 如果文件内容不为空，则表示找到了正确的编码
            if content:
                with codecs.open(input_file, 'w', 'utf-8') as fd:
                    fd.write(content)
                return True

        except Exception as e:
            continue
    # 如果所有编码都无法正常读取，则返回 False
    return False

def get_srt_endtime(input_subtitle_path):
    try:
        with open(input_subtitle_path, 'r', encoding='UTF-8') as f:
            subtitle_data = f.readlines()
    except UnicodeDecodeError:
        detect_and_convert_encoding(input_subtitle_path)
        with open(input_subtitle_path, 'r', encoding='UTF-8') as f:
            subtitle_data = f.readlines()
    # 提取时间点并修改
    count = 0
    for line in subtitle_data:
        if '-->' in line:
            count += 1
            start, end = line.split(' --> ')  # 开始结束时间
            if count == line_count:
                start_h, start_m, start_s, start_ms = re.split(r'[:,.]', start)  # 开始时间
                start_total_ms = int(start_h) * 3600000 + int(start_m) * 60000 + int(start_s) * 1000 + int(start_ms)
                return int(start_total_ms)

def get_ass_endtime(input_subtitle_path):
    try:
        with open(input_subtitle_path, 'r', encoding='UTF-8') as f:
            subtitle_data = f.readlines()
    except UnicodeDecodeError:
        detect_and_convert_encoding(input_subtitle_path)
        with open(input_subtitle_path, 'r', encoding='UTF-8') as f:
            subtitle_data = f.readlines()
    # 提取时间点并修改
    count = 0
    for line in subtitle_data:
        if 'Dialogue' in line:
            count += 1
            if count == line_count:
                start, end = re.findall('(\d+:\d+:\d+\.\d+)',line)  # 开始结束时间
                start_h, start_m, start_s, start_ms = re.split(r'[:.]', start)  # 开始时间
                start_ms = float(f'0.{start_ms}') * 1000
                start_total_ms = int(start_h) * 3600000 + int(start_m) * 60000 + int(start_s) * 1000 + int(start_ms)
                return int(start_total_ms)

class VideoSubtitleProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("字幕时间轴同步工具")
        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(),'w') as f:
                f.write('')
        self.config = configparser.ConfigParser(default_section='Settings')
        self.config.read(self.get_ini_path())  # 读取配置文件
        self.folder_path = tk.StringVar()
        self.progress_text = tk.StringVar()
        self.subtitle_ext_list = ['.srt', '.ass', '.zh.srt', '.zh.ass', 'chs.srt', '.chs.ass']
        self.folder_path.set(self.config.get('Settings', 'last_folder', fallback=''))
        self.folder_path.trace_add("write", self.folder_path_changed)  # 绑定变量变化的回调函数
        self.create_widgets()

    def create_widgets(self):
        frame_folder = ttk.LabelFrame(self.root, text="选择文件夹")
        frame_folder.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_folder, text="文件夹路径：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_folder, textvariable=self.folder_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_folder, text="浏览", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=5)
        tk.Button(button_frame, text="开始同步", command=self.start_processing).pack(side=tk.LEFT, padx=10,pady=10)
        tk.Button(button_frame, text="备份字幕", command=self.start_to_backup).pack(side=tk.LEFT, padx=10,pady=10)
        tk.Button(button_frame, text="重置字幕", command=self.start_to_reset).pack(side=tk.LEFT, padx=10,pady=10)

        frame_output = ttk.LabelFrame(self.root, text="处理日志")
        frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(frame_output, wrap=tk.NONE,height=10)
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # 监听文本框内容变化事件
        self.output_text.bind("<Configure>", self.on_text_changed)

        tk.Label(frame_output, textvariable=self.progress_text).pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def on_text_changed(self,event):
        self.output_text.yview_moveto(1.0)  # 将文本框滚动到底部

    def folder_path_changed(self, *args):
        # 这个函数会在文件夹路径变化时触发
        folder_path = self.folder_path.get()
        # 保存文件夹路径到配置文件
        folder_root = os.path.dirname(folder_path)
        self.config.set('Settings', 'last_folder', folder_root)
        with open(self.get_ini_path(), 'w') as configfile:
            self.config.write(configfile)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.folder_path.get())  # 设置initialdir为当前文件夹路径
        if folder_selected:
            self.folder_path.set(folder_selected)

    def start_to_reset(self):
        self.process_thread = threading.Thread(target=self.reset_subtitle)
        self.process_thread.start()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END,'开始重置字幕...\n')

    def reset_subtitle(self):
        self.progress_text.set('开始重置字幕...')
        for root, dirs, files in os.walk(self.folder_path.get()):
            for file in files:
                if 'SubBackup' in root:
                    break
                if file.endswith('srt') or file.endswith('ass'):
                    file_path = os.path.join(root,file)
                    os.remove(os.path.join(file_path))
                    self.output_text.insert(tk.END,f'已删除字幕:{file}\n')

        bakcup_root_dir = os.path.join(self.folder_path.get(),'SubBackup')
        for root, dirs, files in os.walk(bakcup_root_dir):
            for file in files:
                if file.endswith('srt') or file.endswith('ass'):
                    file_path = os.path.join(root,file)
                    rel_path = os.path.relpath(file_path,bakcup_root_dir)
                    subtitle_path = os.path.join(self.folder_path.get(),os.path.dirname(rel_path),file)
                    shutil.copy(file_path,subtitle_path)
                    self.output_text.insert(tk.END,f'已添加字幕:{file}\n')
        self.progress_text.set('重置成功')


    def start_to_backup(self):
        self.process_thread = threading.Thread(target=self.backup_subtitle)
        self.process_thread.start()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END,'开始备份字幕...\n')


    def backup_subtitle(self):
        # dirname = os.path.basename(self.folder_path.get())
        count = 0
        for root, dirs, files in os.walk(self.folder_path.get()):
            for file in files:
                if 'SubBackup' in root:
                    break
                if file.endswith('srt') or file.endswith('ass'):
                    file_path = os.path.join(root,file)
                    rel_path = os.path.relpath(file_path,self.folder_path.get())
                    bakcup_root_dir = os.path.join(self.folder_path.get(),'SubBackup')
                    bakcup_path_dir = os.path.join(bakcup_root_dir,os.path.dirname(rel_path))
                    if not os.path.exists(bakcup_root_dir):
                        os.mkdir(bakcup_root_dir)
                    if not os.path.exists(bakcup_path_dir):
                        os.mkdir(bakcup_path_dir)
                    file_bakcup_path = os.path.join(bakcup_path_dir,file)
                    if not os.path.exists(file_bakcup_path):
                        # os.rename(file_path,file_bakcup_path)
                        shutil.copy(file_path,file_bakcup_path)
                        self.output_text.insert(tk.END,f'字幕备份成功:{file}\n')
                        count += 1
        self.output_text.insert(tk.END,f'字幕备份成功:共备份{count}个字幕\n')


    def start_processing(self):
        if not self.folder_path.get():
            self.update_status('请先选择一个文件夹。')
            return

        self.process_thread = threading.Thread(target=self.process_videos)
        self.process_thread.start()

    def sub_offset(self,file_path,time_delay):
        if file_path.endswith('.ass') :
            self.shift_subtitle_timeline_ass(file_path,time_delay)
        elif file_path.endswith('.srt'):
            self.shift_subtitle_timeline_srt(file_path,time_delay)

    def get_offset(self,old_file,new_file):
        if old_file.endswith('.srt'):
            old_endtime = get_srt_endtime(old_file)
            new_endtime = get_srt_endtime(new_file)
        elif old_file.endswith('.ass'):
            old_endtime = get_ass_endtime(old_file)
            new_endtime = get_ass_endtime(new_file)
        return new_endtime - old_endtime

    def process_videos(self):
        self.output_text.delete(1.0, tk.END)
        for root, dirs, files in os.walk(self.folder_path.get()):
            for video_file in files:
                if video_file.lower().endswith(('.avi', '.mkv', '.wmv', '.mp4', '.mpeg', '.m4v')):
                    video_filepath = os.path.join(root, video_file)
                    video_name = os.path.splitext(video_filepath)[0]
                    subtitle_path_list = [f'{video_name}{i}' for i in self.subtitle_ext_list]
                    for subtitle_path in subtitle_path_list:
                        if os.path.exists(subtitle_path):
                            file_name, ext = os.path.splitext(subtitle_path)
                            new_subtitle_path = f'{file_name}.new{ext}'
                            # new_subtitle_path = f'temp{ext}'
                            self.progress_text.set("正在获取字幕时间轴偏移量...")
                            if current_os == "Windows":
                                cmd = [alass_path_win, video_filepath, subtitle_path, new_subtitle_path,"-l"]
                                subprocess.call(cmd)
                            elif current_os == "Darwin":
                                working_directory = alass_path_mac
                                os.chdir(working_directory)
                                command = f'cargo run -- "{video_filepath}" "{subtitle_path}" "{new_subtitle_path}" -l'
                                subprocess.run(command, shell=True)
                            offset_time = self.get_offset(subtitle_path,new_subtitle_path)
                            self.output_text.insert(tk.END,f'{offset_time}\n')
                            if abs(offset_time) > 1000:
                                continue
                            if offset_time != 0:
                                self.output_text.insert(tk.END,f'获取字幕偏移量成功: {subtitle_path}\n字幕时间偏移量为:{offset_time}ms\n开始同步字幕...')
                                self.progress_text.set("开始同步字幕...")
                                self.sub_offset(subtitle_path,offset_time)
                                self.output_text.insert(tk.END,'同步成功\n')
                                self.progress_text.set("同步成功")
                            else:
                                self.output_text.insert(tk.END,f'{subtitle_path}字幕时间偏移量为0,不需要同步.\n')
                                self.sub_offset(subtitle_path,offset_time)
                            os.remove(new_subtitle_path)

    def get_ini_path(self,*args):
        # 获取当前.py文件的绝对路径
        current_script = os.path.abspath(__file__)
        ini_path = current_script.replace('.py','.ini')
        return(ini_path)

    def shift_subtitle_timeline_srt(self,input_subtitle_path, shift_second):
        # 输入字幕路径
        if input_subtitle_path == 0:
            input_subtitle_path = input('请输入字幕文件路径：').replace('"', '')
        # 获取字幕内容
        try:
            with open(input_subtitle_path, 'r', encoding='UTF-8') as f:
                subtitle_data = f.readlines()
        except UnicodeDecodeError:
            detect_and_convert_encoding(input_subtitle_path)
            with open(input_subtitle_path, 'r', encoding='UTF-8') as f:
                subtitle_data = f.readlines()
        # 提取时间点并修改
        for line in subtitle_data:
            if '-->' in line:
                where = subtitle_data.index(line)  # 标记索引
                start, end = line.split(' --> ')  # 开始结束时间
                start_h, start_m, start_s, start_ms = re.split(r'[:,.]', start)  # 开始时间
                end_h, end_m, end_s, end_ms = re.split(r'[:,.]', end)  # 结束时间
                start_total_ms = int(start_h) * 3600000 + int(start_m) * 60000 + int(start_s) * 1000 + int(start_ms)
                end_total_ms = int(end_h) * 3600000 + int(end_m) * 60000 + int(end_s) * 1000 + int(end_ms)
                if start_total_ms + shift_second >= 0:
                    start_total_ms = start_total_ms + shift_second  # 添加了移动时间的开始时间
                    end_total_ms = end_total_ms + shift_second  # 添加了移动时间的结束时间
                start_h, remain = divmod(start_total_ms, 3600000)  # 将开始时间转回时、分、秒、毫秒
                start_m, remain = divmod(remain, 60000)
                start_s, remain = divmod(remain, 1000)
                start_ms = remain
                end_h, remain = divmod(end_total_ms, 3600000)  # 将开始时间转回时、分、秒、毫秒
                end_m, remain = divmod(remain, 60000)
                end_s, remain = divmod(remain, 1000)
                end_ms = remain
                start = f'{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d}'
                end = f'{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}'  # 将结束时间换回00:00:00,000格式
                line = start + ' --> ' + end + '\n'
                subtitle_data[where] = line
        with open(input_subtitle_path, 'w', encoding='UTF-8') as f:
            f.write(''.join(subtitle_data))

    def shift_subtitle_timeline_ass(self,input_subtitle_path, shift_second):
        # 输入字幕路径
        if input_subtitle_path == 0:
            input_subtitle_path = input('请输入字幕文件路径：').replace('"', '')
        # 获取字幕内容
        try:
            with open(input_subtitle_path, 'r', encoding='UTF-8') as f:
                subtitle_data = f.readlines()
        except UnicodeDecodeError:
            detect_and_convert_encoding(input_subtitle_path)
            with open(input_subtitle_path, 'r', encoding='UTF-8') as f:
                subtitle_data = f.readlines()
        # 提取时间点并修改
        for line in subtitle_data:
            if 'Dialogue' in line:
                where = subtitle_data.index(line)  # 标记索引
                # line = line.replace('\n', '')  # 去掉换行符
                start, end = re.findall('(\d+:\d+:\d+\.\d+)',line)  # 开始结束时间
                old_time = f"{start},{end}"
                start_h, start_m, start_s, start_ms = re.split(r'[:.]', start)  # 开始时间
                end_h, end_m, end_s, end_ms = re.split(r'[:.]', end)  # 结束时间
                start_ms = float(f'0.{start_ms}') * 1000
                end_ms = float(f'0.{end_ms}') * 1000
                start_total_ms = int(start_h) * 3600000 + int(start_m) * 60000 + int(start_s) * 1000 + int(start_ms)
                end_total_ms = int(end_h) * 3600000 + int(end_m) * 60000 + int(end_s) * 1000 + int(end_ms)
                if start_total_ms + shift_second >= 0:
                    start_total_ms = start_total_ms + shift_second  # 添加了移动时间的开始时间
                    end_total_ms = end_total_ms + shift_second  # 添加了移动时间的结束时间
                start_h, remain = divmod(start_total_ms, 3600000)  # 将开始时间转回时、分、秒、毫秒
                start_m, remain = divmod(remain, 60000)
                start_s, remain = divmod(remain, 1000)
                start_ms = int(remain / 10)
                end_h, remain = divmod(end_total_ms, 3600000)  # 将开始时间转回时、分、秒、毫秒
                end_m, remain = divmod(remain, 60000)
                end_s, remain = divmod(remain, 1000)
                end_ms = int(remain / 10)
                start = f'{start_h:02d}:{start_m:02d}:{start_s:02d}.{start_ms:02d}'
                end = f'{end_h:02d}:{end_m:02d}:{end_s:02d}.{end_ms:02d}'  # 将结束时间换回00:00:00,000格式
                new_time = f"{start},{end}"
                line = line.replace(old_time,new_time)
                subtitle_data[where] = line
        with open(input_subtitle_path, 'w', encoding='UTF-8') as f:
            f.write(''.join(subtitle_data))

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSubtitleProcessor(root)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 600
    wh = 450
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    root.mainloop()