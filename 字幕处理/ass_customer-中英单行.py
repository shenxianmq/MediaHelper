import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import re
import time
import codecs
import threading
import configparser


def detect_and_convert_encoding(input_file):
    encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]

    for enc in encodings:
        try:
            with codecs.open(input_file, mode="r", encoding=enc) as fd:
                content = fd.read()

            # 如果文件内容不为空，则表示找到了正确的编码
            if content:
                with codecs.open(input_file, "w", "utf-8") as fd:
                    fd.write(content)
                return True

        except Exception as e:
            continue
    # 如果所有编码都无法正常读取，则返回 False
    return False


class SubtitleModifier:
    def __init__(self, root):
        self.root = root
        self.root.title("字幕修改工具")
        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(), "w") as f:
                f.write("")
        self.config = configparser.ConfigParser(default_section="Settings")
        self.config.read(self.get_ini_path())  # 读取配置文件

        self.folder_path = tk.StringVar()
        self.double_language = tk.BooleanVar()
        self.font_bold = tk.BooleanVar()
        self.font_name = tk.StringVar()
        self.font_size = tk.StringVar()
        self.out_line = tk.StringVar()
        self.margin_v = tk.StringVar()
        self.english_colour = tk.StringVar()
        self.chi_border_colour = tk.StringVar()
        self.font_border_options = ["黑色", "蓝色"]
        self.font_dict = {
            "华文楷体": "STKaiti",
            "方正黑体": "FZHei-B01S",
            "方正综艺简体": "FZZongYi-M05S",
            "微软雅黑": "Microsoft Yahei",
            "Arial": "Arial",
        }
        self.chi_colour_dict = {
            "黑色": "&H00000000,&H32000000",
            "蓝色": "&H006C3300,&H00000000",
        }

        # 初始化选项的默认值
        self.double_language.set(True)
        self.font_bold.set(False)
        self.font_options = ["Arial", "华文楷体", "微软雅黑", "方正黑体"]
        self.english_options = ["明黄", "橙黄", "暗黄", "白色"]
        self.eng_colour_dict = {
            "明黄": "&H3CF1F3",
            "橙黄": "&H0080FF",
            "暗黄": "&H62A8EB",
            "白色": "&H00FFFFFF",
        }
        self.font_name.set("微软雅黑")
        self.font_size.set("20")
        self.out_line.set("0.5")
        self.margin_v.set("25")
        self.english_colour.set("明黄")
        self.chi_border_colour.set("黑色")

        # 设置文件夹路径为上次保存的路径，如果没有则默认为空
        self.folder_path.set(self.config.get("Settings", "last_folder", fallback=""))
        self.create_widgets()
        self.folder_path.trace_add("write", self.folder_path_changed)  # 绑定变量变化的回调函数
        self.double_language.trace_add("write", self.double_language_changed)

    def create_widgets(self):
        frame_file = ttk.LabelFrame(self.root, text="选择文件夹")
        frame_file.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_file, text="文件夹路径：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_file, textvariable=self.folder_path, width=40).grid(
            row=0, column=1, padx=5, pady=5
        )
        tk.Button(frame_file, text="浏览", command=self.browse_file_or_folder).grid(
            row=0, column=2, padx=5, pady=5
        )

        frame_options = ttk.LabelFrame(self.root, text="修改选项")
        frame_options.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        i = 0
        tk.Checkbutton(frame_options, text="双语类型", variable=self.double_language).grid(
            row=i, column=0, padx=5, pady=5
        )
        tk.Checkbutton(frame_options, text="加粗", variable=self.font_bold).grid(
            row=i, column=1, padx=5, pady=5
        )
        i += 1

        tk.Label(frame_options, text="字体名称：").grid(row=i, column=0, padx=5, pady=5)
        tk.OptionMenu(frame_options, self.font_name, *self.font_options).grid(
            row=i, column=1, padx=5, pady=5
        )
        i += 1

        tk.Label(frame_options, text="中文颜色：").grid(row=i, column=0, padx=5, pady=5)
        tk.OptionMenu(
            frame_options, self.chi_border_colour, *self.font_border_options
        ).grid(row=i, column=1, padx=5, pady=5)
        i += 1

        tk.Label(frame_options, text="英文颜色：").grid(row=i, column=0, padx=5, pady=5)
        tk.OptionMenu(frame_options, self.english_colour, *self.english_options).grid(
            row=i, column=1, padx=5, pady=5
        )
        i += 1

        tk.Label(frame_options, text="字体大小：").grid(row=i, column=0, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.font_size, width=10).grid(
            row=i, column=1, padx=5, pady=5
        )
        i += 1

        tk.Label(frame_options, text="边框大小：").grid(row=i, column=0, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.out_line, width=10).grid(
            row=i, column=1, padx=5, pady=5
        )
        i += 1

        tk.Label(frame_options, text="下边距：").grid(row=i, column=0, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.margin_v, width=10).grid(
            row=i, column=1, padx=5, pady=5
        )

        tk.Button(self.root, text="开始修改", command=self.start_modify).pack(pady=10)

        self.output_text = tk.Text(self.root, wrap=tk.WORD, height=12)
        self.output_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def browse_file_or_folder(self):
        path = filedialog.askdirectory(initialdir=self.folder_path.get())
        if path:
            self.folder_path.set(path)

    def insert_message(self, message):
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)

    def get_ini_path(self, *args):
        # 获取当前.py文件的绝对路径
        current_script = os.path.abspath(__file__)
        # 获取文件名（不包括后缀）
        ini_path = current_script.replace(".py", ".ini")
        return ini_path

    def folder_path_changed(self, *args):
        # 这个函数会在文件夹路径变化时触发
        folder_path = self.folder_path.get()
        # 保存文件夹路径到配置文件
        folder_root = os.path.dirname(folder_path)
        self.config.set("Settings", "last_folder", folder_root)
        with open(self.get_ini_path(), "w") as configfile:
            self.config.write(configfile)

    def double_language_changed(self, *args):
        double_language = self.double_language.get()
        if double_language:
            self.font_name.set("微软雅黑")
            self.margin_v.set("25")
            self.font_bold.set(False)
        else:
            self.font_name.set("微软雅黑")
            self.margin_v.set("35")
            self.font_bold.set(False)

    def start_modify(self):
        folder_path = self.folder_path.get()
        double_language = self.double_language.get()
        font_name = self.font_dict[self.font_name.get()]
        font_size = self.font_size.get()
        out_line = self.out_line.get()
        margin_v = self.margin_v.get()
        chi_border_colour = self.chi_colour_dict[self.chi_border_colour.get()]
        english_colour = self.eng_colour_dict[self.english_colour.get()]
        self.output_text.delete(1.0, tk.END)

        if not folder_path:
            tk.messagebox.showerror("错误", "请选择文件夹")
            return

        if os.path.isdir(folder_path):
            thread = threading.Thread(
                target=self.modify_subtitles_in_folder,
                args=(
                    folder_path,
                    double_language,
                    chi_border_colour,
                    font_name,
                    font_size,
                    out_line,
                    margin_v,
                    english_colour,
                ),
            )
            thread.start()
        else:
            tk.messagebox.showerror("错误", "无效的文件夹路径")

    def modify_subtitle(
        self,
        ass_path,
        double_language,
        chi_border_colour,
        font_name,
        font_size,
        out_line,
        margin_v,
        english_colour,
    ):
        try:
            try:
                with open(ass_path, "r", encoding="utf-8") as f:
                    sub_text = f.read()
            except:
                detect_and_convert_encoding(ass_path)
                time.sleep(5)
                with open(ass_path, "r", encoding="utf-8") as f:
                    sub_text = f.read()
            font_size_eng = str(int(int(font_size) * 0.618) + 1)
            font_bold = "-1" if self.font_bold.get() else "0"
            chi_eng_style = f"Style: Default,{font_name},{font_size},&H00FFFFFF,&HF0000000,{chi_border_colour},{font_bold},0,0,0,100,100,0,0,1,{out_line},0,2,5,5,{int(margin_v)+12},134\nStyle: Eng,Microsoft Yahei,{font_size_eng},{english_colour},&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0.5,0,2,0,0,{margin_v},1"
            chi_style = f"Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,{chi_border_colour},{font_bold},0,0,0,100,100,0,0,1,{out_line},0,2,5,5,{margin_v},134"
            sub_text = re.sub("Style:.*?\n", "", sub_text)
            sub_text = re.sub("{[^}]+}", "", sub_text)
            # 修改字幕文件分辨率
            pattern = r"\[Script Info\].*?\[V4\+ Styles\]"
            replacement = rf"[Script Info]\nTitle:\nScriptType: v4.00+\nCollisions: Normal\nPlayDepth: 0\nPlayResX: 384\nPlayResY: 288\nScaledBorderAndShadow: yes\nTimer: 100.0000\n\n[V4+ Styles]"
            sub_text = re.sub(pattern, replacement, sub_text, flags=re.DOTALL)

            if double_language:
                default_style = chi_eng_style
                sub_text = re.sub("Encoding", f"Encoding\n{default_style}", sub_text)
                # sub_text = sub_text.replace("Default,,0,0,0,,", "Default,NTP,0,0,0,,")
                sub_text = re.sub(
                    r"(Dialogue:[^,]+,[^,]+,[^,]+,).*?,,",
                    r"\1Default,NTP,0,0,0,,",
                    sub_text,
                )
                with open(ass_path, "w", encoding="utf-8") as f:
                    f.write(sub_text)
                if "\\N" in sub_text:
                    self.double_language_process(ass_path)
            else:
                default_style = chi_style
                sub_text = re.sub("Encoding", f"Encoding\n{default_style}", sub_text)
                # sub_text = sub_text.replace("Default,,0,0,0,,", "Default,NTP,0,0,0,,")
                sub_text = re.sub(
                    r"(Dialogue:[^,]+,[^,]+,[^,]+,).*?,,",
                    r"\1Default,NTP,0,0,0,,",
                    sub_text,
                )
                with open(ass_path, "w", encoding="utf-8") as f:
                    f.write(sub_text)
            return True
        except Exception as e:
            self.insert_message(f"字幕修改失败:{e}\n")
            return False

    def double_language_process(self, ass_path):
        res = ""
        with open(ass_path, "r", encoding="utf-8") as input_file:
            # 遍历输入文件的每一行
            for line in input_file:
                # 使用正则表达式匹配并分割每一行的内容
                if "\\N" in line:
                    pattern = r"(Dialogue:.*?0*,0*,0*,,)(.*?)\\N(.*)"
                    matches = re.match(pattern, line)

                    # 如果匹配成功
                    if matches:
                        # 获取匹配的三部分内容
                        dialogue_chi = matches.group(1)
                        dialogue_eng = dialogue_chi.replace("Default", "Eng").replace(
                            "Dialogue: 0", "Dialogue: 1"
                        )
                        chi_text = matches.group(2)
                        eng_text = matches.group(3).replace("{\\rEng}", "")

                        # 拼接成新的文本
                        new_line = (
                            f"{dialogue_chi}{chi_text}\n{dialogue_eng}{eng_text}\n"
                        )
                    else:
                        # 如果匹配失败，则保留原始行
                        new_line = line
                    # 将处理后的行写入输出文件
                else:
                    new_line = line
                res += new_line
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(res)

    def modify_subtitles_in_folder(
        self,
        folder_path,
        double_language,
        chi_border_colour,
        font_name,
        font_size,
        out_line,
        margin_v,
        english_colour,
    ):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".ass"):
                    file_path = os.path.join(root, file)
                    success = self.modify_subtitle(
                        file_path,
                        double_language,
                        chi_border_colour,
                        font_name,
                        font_size,
                        out_line,
                        margin_v,
                        english_colour,
                    )
                    if success:
                        self.insert_message(f"{file_path}: 字幕修改成功\n")
                    else:
                        self.insert_message(f"{file_path}: 字幕修改失败\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleModifier(root)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 600
    wh = 500
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    root.mainloop()
