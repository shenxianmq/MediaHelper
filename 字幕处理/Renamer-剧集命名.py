from genericpath import isdir
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import os
import re
import configparser


class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer")
        self.file_list = []
        self.tv_name_entry = tk.StringVar()
        self.ep_pattern = tk.StringVar()
        self.ep_pattern_options = tk.StringVar()
        self.season_pattern = tk.StringVar()
        self.config = ""
        self.tv_name = ""
        self.multiple = tk.BooleanVar()
        self.chinse_num = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        self.ext_list = [".mkv", ".mp4", ".srt", ".ass", ".ts", ".rmvb"]
        self._numbers_re = r"\d+|[一二三四五六七八九十]+"
        self._season_re = r"(?:第)?\s*(?:\d+|[一二三四五六七八九十]+)\s*(季)"
        self._season_re_2 = r"(?<![a-zA-Z0-9_])[sS](eason)?\s*0*\d+"
        self._episodes_re = r"(?:第)?\s*(?<![sS])(?:\d+|[一二三四五六七八九十]+)\s*(?:集|话|話)?\s*.\s*(?:第)?\s*(?:\d+|[一二三四五六七八九十]+)\s*(?:集|话|話)"
        self._episodes_re_2 = (
            r"(?:[Ee]0*|episode|ep)([0-9]+)\s*\.\s*(?:[Ee]0*|episode|ep)([0-9]+)"
        )
        self._episode_re = r"(?<![a-zA-Z0-9_])(?:e|ep|episode)\s*0*\d+"
        self._episode_re_2 = r"(?:第)?\s*(?:\d+|[一二三四五六七八九十]+)\s*(?:集|话|話)"
        self.folder_list = []
        self.load_config()
        self.folder_path = self.config.get("Settings", "last_folder", fallback="")
        self.create_gui()

    def create_gui(self):
        # 创建和布局 GUI 元素
        frame_options = ttk.LabelFrame(self.root, text="集数定位")
        frame_options.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        tk.Checkbutton(frame_options, text="批量处理", variable=self.multiple).grid(
            row=0, column=1, padx=5, pady=5
        )
        self.multiple.set(False)
        tk.Label(frame_options, text="剧集名:").grid(row=1, column=1, padx=10, pady=5)
        tk.Entry(frame_options, textvariable=self.tv_name_entry, width=40).grid(
            row=1, column=2, padx=10, pady=5
        )
        tk.Label(frame_options, text="匹配季数:").grid(row=2, column=1, padx=10, pady=5)
        tk.Entry(frame_options, textvariable=self.season_pattern, width=40).grid(
            row=2, column=2, padx=10, pady=5
        )
        self.season_pattern.set(f"({self._season_re}|{self._season_re_2})")
        tk.Label(frame_options, text="匹配集数:").grid(row=3, column=1, padx=10, pady=5)
        tk.Entry(frame_options, textvariable=self.ep_pattern, width=40).grid(
            row=3, column=2, padx=10, pady=5
        )
        # self.ep_pattern.set(r'(S\d+)?[第eEP]?0*(\d+)集?[话話]?')
        self.ep_pattern.set(f"({self._episode_re}|{self._episode_re_2})")
        tk.Label(frame_options, text="集数正则:").grid(row=4, column=1, padx=10, pady=5)
        tk.Entry(frame_options, textvariable=self.ep_pattern_options, width=40).grid(
            row=4, column=2, padx=10, pady=5
        )
        self.ep_pattern_options.set("第0*(\d+)[集话話回] | [eEP]0*(\d+)")
        # 创建文件列表框，用于显示文件列表

        frame_output = ttk.LabelFrame(self.root, text="文件信息")
        frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.file_listbox = tk.Listbox(frame_output, width=50, height=10)
        self.file_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=5)

        tk.Button(button_frame, text="添加文件夹", command=self.start_to_browse_folder).pack(
            side=tk.LEFT, padx=10, pady=10
        )
        tk.Button(button_frame, text="改名预览", command=self.preview_rename).pack(
            side=tk.LEFT, padx=10, pady=10
        )
        tk.Button(button_frame, text="重命名文件", command=self.start_to_rename).pack(
            side=tk.LEFT, padx=10, pady=10
        )
        tk.Button(button_frame, text="清空文件", command=self.empty_file_list).pack(
            side=tk.LEFT, padx=10, pady=10
        )

    def get_ini_path(self, *args):
        # 获取当前.py文件的绝对路径
        current_script = os.path.abspath(__file__)
        ini_path = current_script.replace(".py", ".ini")
        return ini_path

    def load_config(self):
        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(), "w") as f:
                f.write("")
        self.config = configparser.ConfigParser(default_section="Settings")
        self.config.read(self.get_ini_path())  # 读取配置文件

    def start_to_browse_folder(self):
        thread = threading.Thread(target=self.browse_folder, args=())
        thread.start()

    def browse_folder(self):
        self.folder_list = []
        self.file_list = []
        self.file_listbox.delete(0, tk.END)
        folder_path = filedialog.askdirectory(initialdir=self.folder_path)
        folder_root = os.path.dirname(folder_path)
        self.config.set("Settings", "last_folder", folder_root)
        with open(self.get_ini_path(), "w") as configfile:
            self.config.write(configfile)
        if self.multiple.get():
            self.folder_list = [
                os.path.join(folder_path, i)
                for i in os.listdir(folder_path)
                if os.path.isdir(os.path.join(folder_path, i))
            ]
        else:
            self.folder_list.append(folder_path)
        self.tv_name = os.path.basename(folder_path)
        for folder_path in self.folder_list:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    last_dir = os.path.basename(os.path.dirname(file_path))
                    if (
                        os.path.splitext(file_path)[1] in self.ext_list
                        and file_path not in self.file_list
                    ):
                        # print(file_path)
                        self.file_listbox.insert(tk.END, os.path.join(last_dir, file))
                        self.file_list.append(file_path)

    def start_to_rename(self):
        thread = threading.Thread(target=self.rename, args=())
        thread.start()

    def empty_file_list(self):
        self.file_list = []
        self.tv_name_entry.set("")
        self.file_listbox.delete(0, tk.END)

    def get_new_name(self, file, idx):
        ep_pattern = self.ep_pattern.get()
        season_pattern = self.season_pattern.get()
        season_name = os.path.basename(os.path.dirname(file))
        season_name_temp = season_name
        file_name = os.path.join(season_name, os.path.basename(file))
        if self.tv_name_entry.get():
            self.tv_name = self.tv_name_entry.get()
        elif self.multiple.get():
            for folder in sorted(self.folder_list, key=lambda x: len(x), reverse=True):
                if folder in os.path.dirname(file):
                    self.tv_name = os.path.basename(folder)
                    break
        else:
            self.tv_name = os.path.basename(self.folder_list[0])
        for i, chinese_num in enumerate(self.chinse_num):
            file = file.replace(chinese_num, str(i + 1))
            season_name_temp = season_name_temp.replace(chinese_num, str(i + 1))
        ep_num = re.findall(
            rf"{ep_pattern}",
            os.path.splitext(os.path.basename(file).replace("mp4", ""))[0],
        )
        # 如果是ova就直接改为第0集
        if (
            "ova" in os.path.splitext(os.path.basename(file))[0]
            or "OVA" in os.path.splitext(os.path.basename(file))[0]
        ):
            ep_num = "0"
        if ep_num:
            ep_num = ep_num[0]
        else:
            return file_name, file_name
        old_ep_num = ep_num

        if self.tv_name == season_name:
            season_num = "1"
        else:
            season_num = re.findall(rf"{season_pattern}", season_name_temp)
            if season_num:
                season_num = season_num[0]
            else:
                season_num = "1"
        ep_num = ep_num.zfill(2)
        season_num = season_num.zfill(2)
        extension = os.path.splitext(file_name)[1]
        vedio_format = re.findall("720p|1080p|4k", file_name.lower())
        audio_format = re.findall("hevc|avc", file_name.lower())
        new_name = os.path.join(
            season_name, f"{self.tv_name}.S{season_num}E{ep_num}.第{old_ep_num}集"
        )
        if vedio_format:
            new_name = f"{new_name}.{vedio_format[0]}"
        if audio_format:
            new_name = f"{new_name}.{audio_format[0]}"
        new_name = new_name + extension
        if new_name.endswith("ass") and "zh" not in new_name and "chs" not in new_name:
            new_name = new_name.replace(".ass", ".chs.ass")
        if new_name.endswith("srt") and "zh" not in new_name and "chs" not in new_name:
            new_name = new_name.replace(".srt", ".chs.srt")
        return file_name, new_name

    def rename(self):
        files_to_rename = self.file_list[:]
        self.file_listbox.delete(0, tk.END)

        if not files_to_rename:
            self.file_listbox.insert(tk.END, "未选择文件")
            return

        for idx, file in enumerate(files_to_rename):
            dir_path = os.path.dirname(file)
            file_name, new_name = self.get_new_name(file, idx)
            new_name = os.path.basename(new_name)
            new_path = os.path.join(dir_path, new_name)
            os.rename(file, os.path.join(dir_path, new_path))
            self.file_list.remove(file)
            self.file_list.append(new_path)
            self.file_listbox.delete(idx)
            self.file_listbox.insert(idx, new_name)
            self.file_listbox.yview_moveto(1.0)
            print(new_name)
        print("重命名成功")
        self.file_listbox.insert(tk.END, "重命名成功")

    def preview_rename(self):
        files_to_rename = self.file_list[:]
        self.file_listbox.delete(0, tk.END)
        if not files_to_rename:
            self.file_listbox.insert(tk.END, "未选择文件")
            return
        previews = []
        for idx, file in enumerate(files_to_rename):
            file_name, new_name = self.get_new_name(file, idx)
            previews.append(f"{file_name} => {new_name}")
        for res in previews:
            self.file_listbox.insert(tk.END, res)


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
