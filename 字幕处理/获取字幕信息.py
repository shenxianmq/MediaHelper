import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
import threading
import configparser
import re

def get_sub_info(mkv_path):
    ffmpeg_command = ['ffmpeg', '-i', mkv_path]
    output_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'sub_info.txt')
    with open(output_txt_path, 'w', encoding='utf-8') as output_file:
        try:
            subprocess.run(ffmpeg_command, stdout=output_file, stderr=subprocess.STDOUT, text=True, check=True)
        except subprocess.CalledProcessError as e:
            # 如果出现非零返回码，也将错误信息写入文件
            output_file.write(str(e.output))

        # 使用正则表达式提取字幕信息
        with open(output_txt_path, 'r', encoding='utf-8') as f:
            content = f.read().replace("subrip",'srt')
        subtitle_info = []
        lines = content.split('\n')
        for line in lines:
            if re.search(r'Stream #0:\d+\(.*?\): Subtitle: .*', line):
                stream_match = re.search(r'Stream #0:(\d+)\((.*?)\): Subtitle: (.*)', line)
                if stream_match:
                    stream_number = stream_match.group(1).strip()
                    subtitle_lang = stream_match.group(2).strip()
                    subtitle_type = re.sub('\(.*?\)','',stream_match.group(3)).strip()
                    subtitle_info.append([stream_number, subtitle_type, "",subtitle_lang])
            elif re.search(r'title\s+:\s+(.+)', line):
                title_match = re.search(r'title\s+:\s+(.+)', line)
                if title_match and subtitle_info:
                    subtitle_info[-1][2] = title_match.group(1).strip()
        print('字幕信息:\n')
        for index,sub_type,title,subtitle_lang in [item for item in subtitle_info if item[2]]:
            sub_info = f"{int(index.strip())-1}:{title.strip()}.{sub_type}\n"
            print(sub_info)
        chi_sub = [item for item in subtitle_info if "chi" in item[3]]
        chi_sub = [item for item in chi_sub if "简" in item[2] or "Simplified" in item[2] or "chs" in item[2]]
        chi_sub_res = [('1','srt','chi')]
        if chi_sub:
            print(f'找到中文字幕:\n')
            chi_sub_res = chi_sub[:]
        sub_num = str(int(chi_sub_res[0][0])-1)
        sub_ext = chi_sub_res[0][1]
        return str(int(sub_num) - 1),sub_ext

class SubtitleExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("字幕提取工具")

        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(),'w') as f:
                f.write('')
        self.config = configparser.ConfigParser(default_section='Settings')
        self.config.read(self.get_ini_path())  # 读取配置文件

        self.font_types = ["srt","ass"]

        self.folder_path = tk.StringVar()
        self.sub_num = tk.StringVar()
        self.sub_ext = tk.StringVar()
        self.progress_text = tk.StringVar()
        self.auto_process = tk.BooleanVar()

        # 设置文件夹路径为上次保存的路径，如果没有则默认为空
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

        tk.Button(button_frame, text="获取信息", command=self.start_get_sub_info).pack(side=tk.LEFT, padx=10,pady=10)
        tk.Button(button_frame, text="开始提取", command=self.start_extraction).pack(side=tk.LEFT, padx=10,pady=10)


        frame_output = ttk.LabelFrame(self.root, text="处理日志")
        frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(frame_output, wrap=tk.WORD, height=10)
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_output, textvariable=self.progress_text).pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.folder_path.get())  # 设置initialdir为当前文件夹路径
        if folder_selected:
            self.folder_path.set(folder_selected)

    def get_ini_path(self,*args):
        # 获取当前.py文件的绝对路径
        current_script = os.path.abspath(__file__)
        ini_path = current_script.replace('.py','.ini')
        return(ini_path)

    def start_get_sub_info(self):
        folder_path = self.folder_path.get()
        self.progress_text.set("正在获取字幕信息...")
        self.output_text.delete(1.0, tk.END)
        mkv_path = ''
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.mkv') or file.endswith('.mp4'):
                    mkv_path = os.path.join(root, file)
                    break
        if mkv_path:
            thread = threading.Thread(target=self.get_sub_info, args=(mkv_path,))
            thread.start()

    def get_sub_info(self,mkv_path):
        # 定义命令和参数列表
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=index:stream_tags=title',
            '-select_streams', 's',
            mkv_path
        ]

        # 执行命令
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        # 获取输出
        output = result.stdout
        self.output_text.insert(tk.END,f'{output}\n')
        self.progress_text.set(f"字幕信息获取成功")


    def folder_path_changed(self, *args):
        # 这个函数会在文件夹路径变化时触发
        folder_path = self.folder_path.get()
        # 保存文件夹路径到配置文件
        folder_root = os.path.dirname(folder_path)
        self.config.set('Settings', 'last_folder', folder_root)
        with open(self.get_ini_path(), 'w') as configfile:
            self.config.write(configfile)

    def start_extraction(self):
        folder_path = self.folder_path.get()
        sub_num = self.sub_num.get()
        sub_num = str(int(sub_num) - 1)
        sub_ext = self.sub_ext.get()
        auto_process = self.auto_process.get()
        if not folder_path:
            tk.messagebox.showerror("错误", "请选择文件夹")
            return

        if not sub_num:
            tk.messagebox.showerror("错误", "请输入字幕流编号")
            return

        if not sub_ext:
            tk.messagebox.showerror("错误", "请输入字幕格式")
            return

        self.progress_text.set("正在提取字幕...")
        self.output_text.delete(1.0, tk.END)
        thread = threading.Thread(target=self.extract_subtitles, args=(folder_path, sub_num, sub_ext,auto_process))
        thread.start()

    def extract_subtitles(self, folder_path, sub_num, sub_ext,auto_process):
        count = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.mkv') or file.endswith('.mp4'):
                    mkv_path = os.path.join(root, file)
                    if auto_process:
                        sub_num,sub_ext = self.get_sub_info(mkv_path)
                        self.sub_num.set(sub_num)
                        self.sub_ext.set(sub_ext)
                    output_subfile = f'{os.path.splitext(mkv_path)[0]}.chs.{sub_ext}'
                    if os.path.exists(output_subfile):
                        os.remove(output_subfile)
                    cmd = f'ffmpeg -i "{mkv_path}" -map 0:s:{sub_num} "{output_subfile}"'
                    os.system(cmd)
                    count += 1
                    self.progress_text.set(f"已提取 {count} 个字幕")
        self.output_text.insert(tk.END, f"成功提取字幕: {file}\n")

        self.progress_text.set(f"提取完成，共提取 {count} 个字幕")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleExtractor(root)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 600
    wh = 450
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    root.mainloop()