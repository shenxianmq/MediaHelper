import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import configparser
import codecs
import re

#弹幕：Dialogue:.*, 925,.*\n|Dialogue:.*, 950,.*\n|Dialogue:.*, 975,.*\n|Dialogue:.*, 1050,.*\n

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

class AssFileEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Ass-Srt文本替换工具")
        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(),'w') as f:
                f.write('')
        self.config = configparser.ConfigParser(default_section='Settings')
        self.config.read(self.get_ini_path())  # 读取配置文件

        self.folder_path = tk.StringVar()
        self.search_str = tk.StringVar()
        self.replace_str = tk.StringVar()
        self.regex = tk.BooleanVar()
        # 设置文件夹路径为上次保存的路径，如果没有则默认为空
        self.folder_path.set(self.config.get('Settings', 'last_folder', fallback=''))

        self.create_widgets()
        self.folder_path.trace_add("write", self.folder_path_changed)  # 绑定变量变化的回调函数

    def create_widgets(self):
        frame_folder = ttk.LabelFrame(self.root, text="选择文件夹")
        frame_folder.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_folder, text="文件夹路径：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_folder, textvariable=self.folder_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_folder, text="浏览", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)
        # 创建 LabelFrame
        frame_replace = ttk.LabelFrame(root, text="替换设置")
        frame_replace.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # 创建 Checkbutton，并放置在 LabelFrame 的最左边
        checkbutton = tk.Checkbutton(frame_replace, text="正则")
        checkbutton.grid(row=0, column=0, padx=5, pady=5)
        self.regex = tk.BooleanVar()
        checkbutton['variable'] = self.regex
        self.regex.set(False)

        # 第一行
        tk.Label(frame_replace, text="查找：").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(frame_replace, textvariable=self.search_str, width=40).grid(row=1, column=1, padx=5, pady=5)

        # 第二行
        tk.Label(frame_replace, text="替换：").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(frame_replace, textvariable=self.replace_str, width=40).grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.root, text="开始替换", command=self.start_replace_thread).pack(pady=10)

        frame_output = ttk.LabelFrame(self.root, text="处理日志")
        frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(frame_output, wrap=tk.WORD, height=10)
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def get_ini_path(self,*args):
        # 获取当前.py文件的绝对路径
        current_script = os.path.abspath(__file__)
        # 获取文件名（不包括后缀）
        # script_name = os.path.splitext(os.path.basename(current_script))[0] + '.ini'
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

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.folder_path.get())
        if folder_selected:
            self.folder_path.set(folder_selected)

    def replace_files(self):
        folder_path = self.folder_path.get()
        search_str = self.search_str.get()
        replace_str = self.replace_str.get()

        if not folder_path:
            tk.messagebox.showerror("错误", "请选择文件夹")
            return

        if not search_str:
            tk.messagebox.showerror("错误", "请输入要替换的字符串")
            return

        self.output_text.delete(1.0, tk.END)

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.ass') or file.endswith('.srt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        detect_and_convert_encoding(file_path)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    if self.regex:
                        content = re.sub(search_str,replace_str,content)
                    else:
                        content = content.replace(search_str.strip(), replace_str.strip())

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    self.insert_message(f"{file_path}\n替换成功.\n")
                    self.output_text.see(tk.END)
        self.insert_message(f"全部替换完成.\n")

    def insert_message(self,message):
        self.output_text.insert(tk.END,message)
        self.output_text.see(tk.END)

    def start_replace_thread(self):
        # 创建一个线程来执行文件替换任务
        replace_thread = threading.Thread(target=self.replace_files)
        replace_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AssFileEditor(root)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 600
    wh = 450
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    root.mainloop()
