import os
import shutil
import tkinter as tk
import tkinter as ttk
from tkinter import filedialog
import threading
import configparser

def get_desktop_path():
    if os.name == "posix":  # 检查操作系统是否为类Unix系统（包括macOS）
        return os.path.expanduser("~/Desktop")  # macOS的桌面路径
    elif os.name == "nt":  # 检查操作系统是否为Windows
        return os.path.expanduser("~\\Desktop")  # Windows的桌面路径
    else:
        return None  # 其他操作系统返回None或自定义路径

class FileExtractorUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("网盘字幕提取上传工具")
        # 创建配置文件对象
        if not os.path.exists(self.get_ini_path()):
            with open(self.get_ini_path(),'w') as f:
                f.write('')
        self.config = configparser.ConfigParser(default_section='Settings')
        self.config.read(self.get_ini_path())  # 读取配置文件
        self.folder_path = tk.StringVar()

        # 设置文件夹路径为上次保存的路径，如果没有则默认为空
        self.folder_path.set(self.config.get('Settings', 'last_folder', fallback=''))

        # 指定 temp_folder 的路径
        self.temp_folder = os.path.join('/Users/shenxian/Downloads','看剧')  # 在这里指定 temp_folder 的路径

        # 创建GUI界面
        self.create_widgets()

        # 记录上次选择的文件夹路径
        self.folder_path.trace_add("write", self.folder_path_changed)  # 绑定变量变化的回调函数

    def create_widgets(self):
        # 选择文件夹按钮和文本框显示选取的文件夹路径
        frame_folder = ttk.LabelFrame(self.root,borderwidth=0)
        frame_folder.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_folder, text="文件夹路径：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_folder, textvariable=self.folder_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_folder, text="浏览", command=self.select_folder).grid(row=0, column=2, padx=5, pady=5)


        # 创建包含两个按钮的框架并放在主窗口中
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=5)

        tk.Button(button_frame, text="提取", command=self.extract_files).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="上传", command=self.upload_files).pack(side=tk.LEFT, padx=10)

        # 文本框用于显示任务完成情况
        self.textbox = tk.Text(self.root, height=10, width=50)
        self.textbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def select_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.folder_path.get())  # 设置initialdir为当前文件夹路径
        if folder_selected:
            self.folder_path.set(folder_selected)

    def empty_folder(self,folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def folder_path_changed(self, *args):
        # 这个函数会在文件夹路径变化时触发
        folder_path = self.folder_path.get()
        # 保存文件夹路径到配置文件
        folder_root = os.path.dirname(folder_path)
        self.config.set('Settings', 'last_folder', folder_root)
        with open(self.get_ini_path(), 'w') as configfile:
            self.config.write(configfile)

    def get_ini_path(self,*args):
        # 获取当前.py文件的绝对路径
        current_script = os.path.abspath(__file__)
        ini_path = current_script.replace('.py','.ini')
        return(ini_path)

    def extract_files(self):
        if os.path.exists(self.temp_folder):
            self.empty_folder(self.temp_folder)
        else:
            os.mkdir(self.temp_folder)
        self.textbox.delete(1.0, tk.END)
        if not self.folder_path.get():
            self.display_message("请选择文件夹")
            return

        # 创建一个线程来执行提取任务
        extraction_thread = threading.Thread(target=self.perform_extraction)
        extraction_thread.start()

    def perform_extraction(self):
        for root, _, files in os.walk(self.folder_path.get()):
            for folder_name in os.listdir(root):
                folder_path = os.path.join(root, folder_name)
                if os.path.isdir(folder_path):
                    self.start_extract_files(os.path.basename(self.folder_path.get()),folder_path)
        self.display_message("全部提取完成.")

    def start_extract_files(self,root_path, folder_path):
        ass_files = [f for f in os.listdir(folder_path) if f.endswith(".ass") or f.endswith(".srt")]

        if not ass_files:
            return

        # 获取源文件夹的名称
        folder_name = os.path.basename(folder_path)

        # 在 self.temp_folder 下创建与源文件夹同名的文件夹
        target_folder = os.path.join(self.temp_folder,root_path,folder_name)
        os.makedirs(target_folder, exist_ok=True)

        # 复制文件到目标文件夹
        for file in ass_files:
            shutil.copy(os.path.join(folder_path, file), os.path.join(target_folder, file))

        # 写入源文件夹路径到 source_folder.txt
        with open(os.path.join(target_folder, "source_folder.txt"), "w",encoding='utf-8') as f:
            f.write(folder_path)

        self.display_message(f"成功提取：{folder_path}")


    def upload_files(self):
        self.textbox.delete(1.0, tk.END)
        if not os.path.exists(self.temp_folder):
            self.display_message("temp_folder 不存在")
            return

        # 创建一个线程来执行上传任务
        upload_thread = threading.Thread(target=self.perform_upload)
        upload_thread.start()

    def perform_upload(self):
        for root, _, files in os.walk(self.temp_folder):
            for file in files:
                if file.endswith(".ass") or file.endswith(".srt"):
                    source_txt = os.path.join(root, "source_folder.txt")
                    if os.path.exists(source_txt):
                        with open(source_txt, "r",encoding='utf-8') as f:
                            source_folder = f.read()
                        file_path = os.path.join(root, file)
                        upload_filepath = os.path.join(source_folder, file)
                        if os.path.exists(upload_filepath):
                            os.remove(upload_filepath)
                        shutil.copy(file_path, upload_filepath)
                        self.display_message(f"{upload_filepath}上传完成")

        self.display_message("全部上传完成.")

    def display_message(self, message):
        self.textbox.insert(tk.END, message + "\n")
        self.textbox.see(tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = FileExtractorUploader(root)

    # 设置窗口尺寸和居中
    window_width = 600
    window_height = 325
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.mainloop()