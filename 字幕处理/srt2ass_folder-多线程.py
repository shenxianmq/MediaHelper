import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import threading
import re
import codecs
import configparser


class SubtitleConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT转换为ASS工具")

        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(), "w") as f:
                f.write("")
        self.config = configparser.ConfigParser(default_section="Settings")
        self.config.read(self.get_ini_path())  # 读取配置文件
        self.resolution = tk.StringVar()
        self.folder_path = tk.StringVar()
        self.font_name = tk.StringVar()
        self.font_size = tk.StringVar()
        self.margin_v = tk.StringVar()
        self.out_line = tk.StringVar()
        self.font_bold = tk.BooleanVar()
        self.font_border_colour = tk.StringVar()
        self.is_deleted = tk.BooleanVar()
        self.font_border_colour = tk.StringVar()
        self.font_options = ["Arial", "华文楷体", "微软雅黑", "方正黑体"]
        self.font_border_options = ["黑色", "蓝色"]
        # self.colour_dict = {"黑色":"&H00000000,&H00000000","蓝色":"&H00604C24,&H00977736"}
        self.colour_dict = {
            "黑色": "&H00000000,&H00000000",
            "蓝色": "&H006C3300,&H00000000",
        }
        self.resolution_options = ["360p", "720p", "1080p"]
        self.resolution_dict = {
            "360p": "PlayResX: 384\nPlayResY: 288",
            "720p": "PlayResX: 1280\nPlayResY: 720",
            "1080p": "PlayResX: 1920\nPlayResY: 1080",
        }
        self.font_dict = {
            "华文楷体": "STKaiti",
            "方正黑体": "FZHei-B01S",
            "方正综艺简体": "FZZongYi-M05S",
            "微软雅黑": "Microsoft Yahei",
            "Arial": "Arial",
        }
        # 设置文件夹路径为上次保存的路径，如果没有则默认为空
        self.folder_path.set(self.config.get("Settings", "last_folder", fallback=""))

        self.create_widgets()
        self.folder_path.trace_add("write", self.folder_path_changed)  # 绑定变量变化的回调函数
        self.resolution.trace_add("write", self.resolution_changed)  # 绑定变量变化的回调函数

    def create_widgets(self):
        frame_folder = ttk.LabelFrame(self.root, text="选择文件夹")
        frame_folder.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_folder, text="文件夹路径：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_folder, textvariable=self.folder_path, width=40).grid(
            row=0, column=1, padx=5, pady=5
        )
        tk.Button(frame_folder, text="浏览", command=self.browse_folder).grid(
            row=0, column=2, padx=5, pady=5
        )

        frame_options = ttk.LabelFrame(self.root, text="转换选项")
        frame_options.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        i = 0

        tk.Checkbutton(frame_options, text="加粗", variable=self.font_bold).grid(
            row=i, column=0, padx=5, pady=5
        )
        self.font_bold.set(False)
        i += 1

        tk.Label(frame_options, text="分辨率：").grid(row=i, column=0, padx=5, pady=5)
        tk.OptionMenu(frame_options, self.resolution, *self.resolution_options).grid(
            row=i, column=1, padx=5, pady=5
        )
        self.resolution.set("360p")

        tk.Label(frame_options, text="字体颜色：").grid(row=i, column=2, padx=5, pady=5)
        tk.OptionMenu(frame_options, self.font_name, *self.font_options).grid(
            row=i, column=3, padx=5, pady=5
        )
        self.font_name.set("微软雅黑")
        i += 1

        tk.Label(frame_options, text="边框颜色：").grid(row=i, column=0, padx=5, pady=5)
        tk.OptionMenu(
            frame_options, self.font_border_colour, *self.font_border_options
        ).grid(row=i, column=1, padx=5, pady=5)
        self.font_border_colour.set("黑色")

        tk.Label(frame_options, text="字体大小：").grid(row=i, column=2, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.font_size, width=10).grid(
            row=i, column=3, padx=5, pady=5
        )
        self.font_size.set("22")
        i += 1

        tk.Label(frame_options, text="下边距：").grid(row=i, column=0, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.margin_v, width=10).grid(
            row=i, column=1, padx=5, pady=5
        )
        self.margin_v.set("25")

        tk.Label(frame_options, text="边框大小：").grid(row=i, column=2, padx=5, pady=5)
        tk.Entry(frame_options, textvariable=self.out_line, width=10).grid(
            row=i, column=3, padx=5, pady=5
        )
        self.out_line.set("1")
        i += 1

        check_button = tk.Checkbutton(
            frame_options, text="删除源文件", variable=self.is_deleted
        )
        check_button.grid(row=i, column=0, columnspan=1, padx=5, pady=5)
        self.is_deleted.set(False)

        tk.Button(self.root, text="开始转换", command=self.start_conversion).pack(pady=10)
        self.progress_text = tk.Text(self.root, wrap=tk.WORD, height=10)
        self.progress_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.folder_path.get())
        if folder_selected:
            self.folder_path.set(folder_selected)

    def get_ini_path(self, *args):
        # 获取当前.py文件的绝对路径
        current_script = os.path.abspath(__file__)
        # 获取文件名（不包括后缀）
        # script_name = os.path.splitext(os.path.basename(current_script))[0] + '.ini'
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

    def resolution_changed(self, *args):
        resolution = self.resolution.get()
        match resolution:
            case "360p":
                self.font_size.set("20")
                self.margin_v.set("25")

            case "720p":
                self.font_size.set("55")
                self.margin_v.set("35")

            case "1080p":
                self.font_size.set("85")
                self.margin_v.set("65")

    def start_conversion(self):
        folder_path = self.folder_path.get()
        font_bold = "-1" if self.font_bold.get() else "0"
        font_size = self.font_size.get()
        font_border_colour = self.colour_dict[self.font_border_colour.get()]
        margin_v = self.margin_v.get()
        is_deleted = self.is_deleted.get()

        if not folder_path:
            messagebox.showerror("错误", "请选择文件夹")
            return

        if not margin_v:
            messagebox.showerror("错误", "请输入下边距")
            return

        if not font_size:
            messagebox.showerror("错误", "请输入字体大小")
            return

        self.progress_text.delete(1.0, tk.END)  # 清空进度文本框

        thread = threading.Thread(
            target=self.convert_subtitles,
            args=(
                folder_path,
                font_bold,
                font_size,
                font_border_colour,
                margin_v,
                is_deleted,
            ),
        )
        thread.start()

    def convert_subtitles(
        self,
        folder_path,
        font_bold,
        font_size,
        font_border_colour,
        margin_v,
        is_deleted,
    ):
        count = 0
        total_files = 0

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".srt"):
                    total_files += 1

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".srt"):
                    file_path = os.path.join(root, file)
                    output_file = self.srt2ass(
                        file_path,
                        font_bold,
                        font_size,
                        font_border_colour,
                        margin_v,
                        is_deleted,
                    )
                    count += 1
                    self.insert_message(f"字幕转换成功:{file_path}\n")
        self.insert_message(f"转换成功:共转换{total_files}个文件\n")

    def insert_message(self, message):
        self.progress_text.insert(tk.END, message)
        self.progress_text.see(tk.END)

    def srt2ass(
        self, input_file, font_bold, font_size, font_border_colour, margin_v, is_deleted
    ):
        if ".ass" in input_file:
            return input_file

        if not os.path.isfile(input_file):
            print(input_file + " not exist")
            return
        src = self.fileopen(input_file)
        tmp = src[0]
        encoding = src[1]
        src = ""
        utf8bom = ""

        if "\ufeff" in tmp:
            tmp = tmp.replace("\ufeff", "")
            utf8bom = "\ufeff"

        tmp = tmp.replace("\r", "")
        lines = [x.strip() for x in tmp.split("\n") if x.strip()]
        subLines = ""
        tmpLines = ""
        lineCount = 0
        output_file = ".".join(input_file.split(".")[:-1])
        output_file += ".ass"
        output_file = (
            output_file.replace("zh", "default.chs")
            .replace("chs", "default.chs")
            .replace("default.default", "default")
        )

        for ln in range(len(lines)):
            line = lines[ln]
            try:
                if line.isdigit() and re.match("-?\d\d:\d\d:\d\d", lines[(ln + 1)]):
                    if tmpLines:
                        subLines += tmpLines + "\n"
                    tmpLines = ""
                    lineCount = 0
                    continue
                else:
                    if re.match("-?\d\d:\d\d:\d\d", line):
                        line = line.replace("-0", "0")
                        tmpLines += "Dialogue: 0," + line + f",Default,NTP,0,0,0,,"
                    else:
                        if lineCount < 2:
                            tmpLines += line
                        else:
                            tmpLines += r"\N" + line
                    lineCount += 1
                ln += 1
            except Exception as e:
                print(input_file, e)

        subLines += tmpLines + "\n"

        subLines = re.sub(r"\d(\d:\d{2}:\d{2}),(\d{2})\d", "\\1.\\2", subLines)
        subLines = re.sub(r"\s+-->\s+", ",", subLines)
        # replace style
        subLines = re.sub(r"<([ubi])>", "{\\\\\g<1>1}", subLines)
        subLines = re.sub(r"</([ubi])>", "{\\\\\g<1>0}", subLines)
        subLines = re.sub(
            r'<font\s+color="?#(\w{2})(\w{2})(\w{2})"?>',
            "{\\\\c&H\\3\\2\\1&}",
            subLines,
        )
        subLines = re.sub(r"</font>", "", subLines)
        head_str = f"""[Script Info]
; This is an Advanced Sub Station Alpha v4+ script.
Title:
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
{self.resolution_dict[self.resolution.get()]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{self.font_dict[self.font_name.get()]},{font_size},&H00FFFFFF,&H000000FF,{font_border_colour},{font_bold},0,0,0,100,100,0,0,1,{self.out_line.get()},0,2,5,5,{margin_v},134

[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text"""

        output_str = utf8bom + head_str + "\n" + subLines
        output_str = output_str.encode(encoding)

        with open(output_file, "wb") as output:
            output.write(output_str)

        output_file = output_file.replace("\\", "\\\\")
        output_file = output_file.replace("/", "//")
        print(f"字幕转换成功:{input_file}")
        if is_deleted:
            os.remove(input_file)
        return output_file

    def fileopen(self, input_file):
        encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]
        tmp = ""
        for enc in encodings:
            try:
                with codecs.open(input_file, mode="r", encoding=enc) as fd:
                    tmp = fd.read()
                    break
            except:
                continue
        return [tmp, enc]


if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleConverter(root)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 600
    wh = 500
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    root.mainloop()
