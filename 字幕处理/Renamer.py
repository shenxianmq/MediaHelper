import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import pyperclip
import os
import re
import configparser

class FileRenamerApp:
    def __init__(self,root):
        self.root = root
        self.root.title("Renamer")
        self.file_list = []
        self.pattern_entry = tk.StringVar()
        self.replace_entry = tk.StringVar()
        self.insert_text_entry = tk.StringVar()
        self.config = ''
        self.ext_list = ['.mkv','.mp4','.srt','.ass']
        self.load_config()
        self.folder_path = self.config.get('Settings', 'last_folder', fallback='')
        self.create_gui()

    def create_gui(self):
        frame_rename = ttk.LabelFrame(self.root,text="重命名选项")
        frame_rename.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # 添加 GUI 元素，包括模式选择、输入框、按钮等
        self.mode_var = tk.StringVar(value="常规替换")
        mode_label = tk.Label(frame_rename, text="重命名模式:")
        mode_optionmenu = tk.OptionMenu(frame_rename, self.mode_var, "常规替换", "正则替换","添加前缀","添加后缀","序列化")

        # 创建和布局 GUI 元素
        mode_label.grid(row=0, column=0, padx=10, pady=5)
        mode_optionmenu.grid(row=0, column=2, padx=10, pady=5)
        frame_options = ttk.LabelFrame(self.root, text="替换内容")
        frame_options.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_options,text="匹配文本:").grid(row=0, column=1,  padx=10, pady=5)
        tk.Entry(frame_options,textvariable=self.pattern_entry, width=40).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(frame_options,text="替换文本:").grid(row=1, column=1, columnspan=1, padx=10, pady=5)
        tk.Entry(frame_options,textvariable=self.replace_entry, width=40).grid(row=1, column=2,padx=10, pady=5)

        tk.Label(frame_options, text="添加内容:").grid(row=2, column=1, columnspan=1, padx=10, pady=5)
        tk.Entry(frame_options,textvariable=self.insert_text_entry, width=40).grid(row=2, column=2,  padx=10, pady=5)

        # 创建文件列表框，用于显示文件列表

        frame_output = ttk.LabelFrame(self.root, text="文件信息")
        frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(frame_output, width=50, height=10)
        self.file_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=5)
        tk.Button(button_frame, text="添加文件", command=self.browse_files).pack(side=tk.LEFT, padx=10,pady=10)
        tk.Button(button_frame, text="添加文件夹", command=self.browse_folder).pack(side=tk.LEFT, padx=10,pady=10)
        tk.Button(button_frame, text="粘贴文件", command=self.get_clipboard_files).pack(side=tk.LEFT, padx=10,pady=10)
        tk.Button(button_frame, text="改名预览", command=self.preview_rename).pack(side=tk.LEFT, padx=10,pady=10)
        tk.Button(button_frame, text="重命名文件", command=self.start_to_rename).pack(side=tk.LEFT, padx=10,pady=10)
        tk.Button(button_frame, text="清空文件", command=self.empty_file_list).pack(side=tk.LEFT, padx=10,pady=10)

    def get_ini_path(self,*args):
        # 获取当前.py文件的绝对路径
        current_script = os.path.abspath(__file__)
        ini_path = current_script.replace('.py','.ini')
        return(ini_path)

    def load_config(self):
         # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(),'w') as f:
                f.write('')
        self.config = configparser.ConfigParser(default_section='Settings')
        self.config.read(self.get_ini_path())  # 读取配置文件

    def get_clipboard_files(self):
        if len(self.file_list) == 0:
            self.file_listbox.delete(0, tk.END)
        file_paths = []
        clipboard = pyperclip.paste()
        file_list = clipboard.split('\n')
        if file_list:
            temp_list = []
            for file in file_list:
                if os.path.exists(file):
                    if file not in self.file_list:
                        temp_list.append(file)
                else:
                    temp_list = []
                    break
            file_paths.extend(temp_list)
        else:
            if os.path.exists(clipboard) and clipboard not in self.file_list:
                file_paths.append(clipboard)
        if file_paths:
            for path in file_paths:
                if path not in self.file_list:
                    self.file_listbox.insert(tk.END, os.path.basename(path))
                    self.file_list.append(path)

    def browse_files(self):
        if len(self.file_list) == 0:
            self.file_listbox.delete(0, tk.END)
        file_paths = filedialog.askopenfilenames(initialdir=self.folder_path)
        if file_paths:
            folder_root = os.path.dirname(file_paths[0])
            self.config.set('Settings', 'last_folder', folder_root)
            with open(self.get_ini_path(), 'w') as configfile:
                self.config.write(configfile)
            for path in file_paths:
                if path not in self.file_list:
                    self.file_listbox.insert(tk.END, os.path.basename(path))
                    self.file_list.append(path)

    def browse_folder(self):
        if len(self.file_list) == 0:
            self.file_listbox.delete(0, tk.END)
        folder_path = filedialog.askdirectory(initialdir=self.folder_path)
        folder_root = os.path.dirname(folder_path)
        self.config.set('Settings', 'last_folder', folder_root)
        with open(self.get_ini_path(), 'w') as configfile:
            self.config.write(configfile)
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root,file)
                if os.path.splitext(file_path)[1] in self.ext_list and file_path not in self.file_list:
                    print(file_path)
                    self.file_listbox.insert(tk.END, os.path.basename(file_path))
                    self.file_list.append(file_path)

    def start_to_rename(self):
            thread = threading.Thread(target=self.rename, args=())
            thread.start()

    def empty_file_list(self):
        self.file_list = []
        self.file_listbox.delete(0, tk.END)

    def get_new_name(self,file,idx):
        selected_mode = self.mode_var.get()
        pattern = self.pattern_entry.get()
        replace_text = self.replace_entry.get()
        insert_text = self.insert_text_entry.get()
        file_name = os.path.basename(file)
        base_name, extension = os.path.splitext(file_name)
        if selected_mode == "常规替换":
            new_name = base_name.replace(pattern, replace_text) + extension
        elif selected_mode == "正则替换":
            new_name = re.sub(pattern, replace_text, base_name) + extension
        elif selected_mode == "序列化":
            new_name = f"{insert_text}{idx + 1:02d}{extension}"
        elif selected_mode == "添加前缀":
            new_name = f"{insert_text}{base_name}{extension}"
        elif selected_mode == "添加后缀":
            new_name = f"{base_name}{insert_text}{extension}"
        if new_name.endswith('ass') and 'zh' not in new_name and 'chs' not in new_name:
            new_name = new_name.replace('.ass','.zh.ass')
        if new_name.endswith('srt') and 'zh' not in new_name and 'chs' not in new_name:
            new_name = new_name.replace('.srt','.zh.srt')
        return file_name,new_name

    def rename(self):
        files_to_rename = self.file_list[:]
        self.file_listbox.delete(0, tk.END)

        if not files_to_rename:
            self.file_listbox.insert(tk.END, "未选择文件")
            return

        for idx, file in enumerate(files_to_rename):
            dir_path = os.path.dirname(file)
            file_name,new_name = self.get_new_name(file,idx)
            new_path = os.path.join(dir_path,new_name)
            os.rename(file,os.path.join(dir_path,new_path))
            self.file_list.remove(file)
            self.file_list.append(new_path)
            self.file_listbox.delete(idx)
            self.file_listbox.insert(idx, new_name)
        self.file_listbox.insert(tk.END,"重命名成功")

    def preview_rename(self):
        files_to_rename = self.file_list[:]
        self.file_listbox.delete(0, tk.END)
        if not files_to_rename:
            self.file_listbox.insert(tk.END,"未选择文件")
            return
        previews = []
        for idx, file in enumerate(files_to_rename):
            file_name,new_name = self.get_new_name(file,idx)
            previews.append(f"{file_name} => {new_name}")
        for res in previews:
            self.file_listbox.insert(tk.END,res)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 700
    wh = 500
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    root.mainloop()
