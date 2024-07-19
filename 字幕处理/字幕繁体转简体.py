import os
import tkinter as tk
from tkinter import filedialog
import opencc
import threading

class SrtConversionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT文件转换工具")

        # 设置窗口大小和居中显示
        window_width = 600
        window_height = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.folder_path = tk.StringVar()
        self.progress_text = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        folder_label = tk.Label(frame_top, text="选择文件夹路径:")
        folder_label.pack(side=tk.LEFT, padx=(0, 5), anchor="w")

        folder_entry = tk.Entry(frame_top, textvariable=self.folder_path, width=40)
        folder_entry.pack(side=tk.LEFT, padx=(0, 5))

        browse_button = tk.Button(frame_top, text="浏览", command=self.browse_folder)
        browse_button.pack(side=tk.LEFT)

        convert_button = tk.Button(self.root, text="开始转换", command=self.start_conversion)
        convert_button.pack(padx=10, pady=5)

        frame_bottom = tk.Frame(self.root)
        frame_bottom.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        progress_label = tk.Label(frame_bottom, text="处理进度:")
        progress_label.pack(padx=10, pady=(0, 5), anchor="w")

        self.progress_text.set("")
        progress_textbox = tk.Text(frame_bottom, height=10, width=50)
        progress_textbox.pack(padx=10, pady=(0, 5), fill=tk.BOTH, expand=True)
        progress_textbox.config(state=tk.DISABLED)
        progress_textbox.tag_configure("center", justify="center")

        self.progress_textbox = progress_textbox

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def convert_srt_files_to_simplified_chinese(self):
        folder_path = self.folder_path.get()
        if not os.path.isdir(folder_path):
            self.progress_text.set("无效的文件夹路径。")
            return

        # 创建 OpenCC 实例，选择繁体字转换为简体字
        converter = opencc.OpenCC('t2s')

        total_files = 0
        converted_files = 0

        # 遍历文件夹中的所有文件
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.srt') or file.endswith('.ass'):
                    total_files += 1
                    file_path = os.path.join(root, file)

                    # 打开 SRT 文件并读取内容
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            srt_content = f.read()
                    except Exception as e:
                        self.progress_textbox.insert(tk.END, f"{file_path} 错误\n", "center")

                    # 使用 OpenCC 进行繁体到简体中文的转换
                    simplified_chinese = converter.convert(srt_content)

                    # 写回到文件中
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(simplified_chinese)

                    converted_files += 1
                    self.progress_textbox.config(state=tk.NORMAL)
                    self.progress_textbox.insert(tk.END, f"{file_path} 已处理\n", "center")
                    self.progress_textbox.config(state=tk.DISABLED)
                    self.root.update_idletasks()

        self.progress_text.set(f"处理完成，共处理 {converted_files}/{total_files} 个文件")

    def start_conversion(self):
        self.progress_textbox.delete(1.0,tk.END)
        # 创建一个线程来执行转换
        conversion_thread = threading.Thread(target=self.convert_srt_files_to_simplified_chinese)
        conversion_thread.start()

if __name__ == '__main__':
    root = tk.Tk()
    app = SrtConversionApp(root)
    root.mainloop()
