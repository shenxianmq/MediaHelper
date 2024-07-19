import os
import codecs

def detect_and_convert_encoding(input_file):
    encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]

    for enc in encodings:
        try:
            with codecs.open(input_file, mode="r", encoding=enc, errors="ignore") as fd:
                content = fd.read()

            # 如果文件内容不为空，则表示找到了正确的编码
            if content:
                with codecs.open(input_file, 'w', 'utf-8') as fd:
                    fd.write(content)
                return True

        except Exception as e:
            continue
    # 如果所有编码都无法正常读取，则返回 False
    return False

def clean_srt_file(file_path):
    # Open the SRT file for reading
    global ignore_words
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except:
        detect_and_convert_encoding(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

    # Iterate through each line in the file and remove lines with Japanese characters
    cleaned_lines = []
    for line in lines:
        if not any(i in line for i in ignore_words):
            cleaned_lines.append(line)
    # Write the result back to the original file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)


if __name__ == "__main__":
    folder_path = "/Volumes/dav/115/看剧/links/电影/系列电影/周星驰系列"  # Replace with the folder path containing SRT files
    ignore_words = ['清水啸歌']
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".ass"):
                srt_file_path = os.path.join(root, file)
                clean_srt_file(srt_file_path)
                print(f"Processed file: {srt_file_path}")
