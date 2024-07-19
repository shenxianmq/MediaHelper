import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import re
import threading
import configparser

class SubtitleModifier:
    def __init__(self, root):
        self.root = root
        self.root.title("字幕修改工具")
        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(),'w') as f:
                f.write('')
        self.config = configparser.ConfigParser(default_section='Settings')
        self.config.read(self.get_ini_path())  # 读取配置文件

        self.folder_path = tk.StringVar()
        self.double_language = tk.BooleanVar()
        self.font_name = tk.StringVar()
        self.font_size = tk.StringVar()
        self.out_line = tk.StringVar()
        self.margin_v = tk.StringVar()

        # 初始化选项的默认值
        self.double_language.set(True)
        self.font_options = ["STKaiti", "Arial", "微软雅黑","方正黑体"]
        self.font_name.set("STKaiti")
        self.font_size.set("22")
        self.out_line.set("1")
        self.margin_v.set("35")

        # 设置文件夹路径为上次保存的路径，如果没有则默认为空
        self.folder_path.set(self.config.get('Settings', 'last_folder', fallback=''))
        self.create_widgets()
        self.folder_path.trace_add("write", self.folder_path_changed)  # 绑定变量变化的回调函数
        self.double_language.trace_add("write", self.double_language_changed)


    def create_widgets(self):
        frame_file = ttk.LabelFrame(self.root, text="选择文件夹")
        frame_file.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_file, text="文件夹路径：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_file, textvariable=self.folder_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_file, text="浏览", command=self.browse_file_or_folder).grid(row=0, column=2, padx=5, pady=5)

        frame_options = ttk.LabelFrame(self.root, text="修改选项")
        frame_options.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Checkbutton(frame_options, text="双语类型", variable=self.double_language).grid(row=0, column=0, padx=5, pady=5)

        # tk.Label(frame_options, text="字体名称：").grid(row=1, column=0, padx=5, pady=5)
        # tk.Entry(frame_options, textvariable=self.font_name, width=20).grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame_options, text="字体名称：").grid(row=1, column=0, padx=5, pady=5)
        tk.OptionMenu(frame_options, self.font_name, *self.font_options).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_options, text="字体大小：").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.font_size, width=10).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame_options, text="边框大小：").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.out_line, width=10).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(frame_options, text="下边距：").grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.margin_v, width=10).grid(row=4, column=1, padx=5, pady=5)

        tk.Button(self.root, text="开始修改", command=self.start_modify).pack(pady=10)

        self.result_text = tk.Text(self.root, wrap=tk.WORD, height=8)
        self.result_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def browse_file_or_folder(self):
        path = filedialog.askdirectory(initialdir=self.folder_path.get())
        if path:
            self.folder_path.set(path)

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

    def double_language_changed(self,*args):
        double_language = self.double_language.get()
        if double_language:
            self.font_name.set('STKaiti')
        else:
            self.font_name.set('Arial')

    def start_modify(self):
        folder_path = self.folder_path.get()
        double_language = self.double_language.get()
        font_name = self.font_name.get()
        font_size = self.font_size.get()
        out_line = self.out_line.get()
        margin_v = self.margin_v.get()
        self.result_text.delete(1.0,tk.END)

        if not folder_path:
            tk.messagebox.showerror("错误", "请选择文件夹")
            return

        if os.path.isdir(folder_path):
            thread = threading.Thread(target=self.modify_subtitles_in_folder, args=(folder_path, double_language, font_name, font_size, out_line, margin_v))
            thread.start()
            # self.modify_subtitles_in_folder(folder_path, double_language, font_name, font_size, out_line, margin_v)
        else:
            tk.messagebox.showerror("错误", "无效的文件夹路径")

    def modify_subtitle(self, ass_path, double_language, font_name, font_size, out_line, margin_v):
        try:
            with open(ass_path, 'r', encoding='utf-8') as f:
                sub_text = f.read()
            font_size_eng = str(int(int(font_size) * 0.618) + 1)
            chi_eng_style = f"Style: Default,{font_name},{font_size},&H00FFFFFF,&HF0000000,&H006C3300,&H00000000,0,0,0,0,100,100,0,0,1,{out_line},0.5,2,5,5,5,134\nStyle: Eng,Cronos Pro Subhead,{font_size_eng},&H3CF1F3,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,2,2,0,0,{margin_v},1"
            # chi_style = f"Style: Default,{font_name},{font_size},&H00FFFFFF,&HF0000000,&H006C3300,&H00000000,0,0,0,0,100,100,0,0,1,{out_line},0.5,2,5,5,{margin_v},134"
            chi_style = f"Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00604C24,&H00977736,-1,0,0,0,100,100,0,0,1,{out_line},0.5,2,5,5,{margin_v},134"
            sub_text = re.sub("Style:.*?\n", "", sub_text)
            sub_text = re.sub("{[^}]+}", "", sub_text)

            if double_language:
                default_style = chi_eng_style
                sub_text = sub_text.replace("\\N", "\\N{\\rEng}")
            else:
                default_style = chi_style

            sub_text = re.sub("Encoding", f"Encoding\n{default_style}", sub_text)

            with open(ass_path, 'w', encoding='utf-8') as f:
                f.write(sub_text)
            return True
        except Exception as e:
            return False

    def modify_subtitles_in_folder(self, folder_path, double_language, font_name, font_size, out_line, margin_v):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".ass"):
                    file_path = os.path.join(root, file)
                    success = self.modify_subtitle(file_path, double_language, font_name, font_size, out_line, margin_v)
                    if success:
                        self.result_text.insert(tk.END, f"{file_path}: 字幕修改成功\n")
                    else:
                        self.result_text.insert(tk.END, f"{file_path}: 字幕修改失败\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleModifier(root)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 600
    wh = 450
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    root.mainloop()
