import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
import threading
import configparser
import codecs
from tkinter.constants import N

def detect_and_convert_encoding(input_file):
    encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]

    for enc in encodings:
        try:
            with codecs.open(input_file, mode="r", encoding=enc) as fd:
                content = fd.read()

            # 如果文件内容不为空，则表示找到了正确的编码
            if content:
                with codecs.open(input_file, 'w', 'utf-8') as fd:
                    fd.write(content)
                return True

        except Exception as e:
            continue

class SubRename:
    def __init__(self, root):
        self.root = root
        self.root.title("字幕重命名")

        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(),'w') as f:
                f.write('')
        self.config = configparser.ConfigParser(default_section='Settings')
        self.config.read(self.get_ini_path())  # 读取配置文件

        self.font_types = ["srt","ass"]

        self.folder_path = tk.StringVar()
        self.progress_text = tk.StringVar()


        # 设置文件夹路径为上次保存的路径，如果没有则默认为空
        self.folder_path.set(self.config.get('Settings', 'last_folder', fallback=''))

        self.create_widgets()
        self.folder_path.trace_add("write", self.folder_path_changed)  # 绑定变量变化的回调函数

    def create_widgets(self):
        frame_option = ttk.LabelFrame(self.root, text="选择文件夹")
        frame_option.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_option, text="文件夹路径：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_option, textvariable=self.folder_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_option, text="浏览", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(frame_option, text="开始转换", command=self.start_rename).grid(row=1, column=1, padx=5, pady=5)

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

    def folder_path_changed(self, *args):
        # 这个函数会在文件夹路径变化时触发
        folder_path = self.folder_path.get()
        # 保存文件夹路径到配置文件
        folder_root = os.path.dirname(folder_path)
        self.config.set('Settings', 'last_folder', folder_root)
        with open(self.get_ini_path(), 'w') as configfile:
            self.config.write(configfile)

    def start_rename(self):
        folder_path = self.folder_path.get()
        if not folder_path:
            tk.messagebox.showerror("错误", "请选择文件夹")
            return

        self.progress_text.set("正在重命名字幕...")
        self.output_text.delete(1.0, tk.END)
        thread = threading.Thread(target=self.rename_sub, args=(folder_path,))
        thread.start()

    def rename_sub(self, folder_path):
        count = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.ass') or file.endswith('.srt'):
                    file_path = os.path.join(root, file)
                    if '.zh' not in file_path:
                        new_file_path = file_path.replace('.ass','.zh.ass').replace('.srt','.zh.srt').replace('.chs','')
                        if os.path.exists(new_file_path):
                            os.remove(new_file_path)
                        os.rename(file_path,new_file_path)
                        count += 1
                        self.progress_text.set(f"重命名 {count} 个字幕")
                        self.output_text.insert(tk.END, f"成功重命名字幕: {file}\n")
                    else:
                        continue
        self.progress_text.set(f"重命名，共重命名 {count} 个字幕")


if __name__ == "__main__":
    root = tk.Tk()
    app = SubRename(root)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 600
    wh = 450
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    root.mainloop()