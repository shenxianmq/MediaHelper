import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

class AssFileEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("ASS文件替换工具")

        self.folder_path = tk.StringVar()
        self.search_str = tk.StringVar()
        self.replace_str = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        frame_folder = ttk.LabelFrame(self.root, text="选择文件夹")
        frame_folder.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_folder, text="文件夹路径：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_folder, textvariable=self.folder_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_folder, text="浏览", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        frame_replace = ttk.LabelFrame(self.root, text="替换设置")
        frame_replace.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(frame_replace, text="要替换的字符串：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_replace, textvariable=self.search_str, width=40).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_replace, text="替换后的字符串：").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(frame_replace, textvariable=self.replace_str, width=40).grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.root, text="开始替换", command=self.replace_files).pack(pady=10)

        frame_output = ttk.LabelFrame(self.root, text="处理日志")
        frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(frame_output, wrap=tk.WORD, height=10)
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
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
                if file.endswith('.ass'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    os.remove(file_path) #挂载的网盘需要先将文件删除后再重新写入才行
                    content = content.replace(search_str, replace_str)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    self.output_text.insert(tk.END, f"{file_path}\n")

        # tk.messagebox.showinfo("完成", "所有文件替换完成")

if __name__ == "__main__":
    root = tk.Tk()
    app = AssFileEditor(root)
    sw = root.winfo_screenwidth()  # 得到屏幕宽度
    sh = root.winfo_screenheight()  # 得到屏幕高度
    ww = 600
    wh = 450
    x = (sw - ww) / 2
    y = (sh - wh) / 2 - 60
    root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))  # 窗口居中
    root.mainloop()
