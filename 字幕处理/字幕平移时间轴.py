import re
import os
import codecs
import pyperclip


def detect_and_convert_encoding(input_file):
    encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]

    for enc in encodings:
        try:
            with codecs.open(input_file, mode="r", encoding=enc, errors="ignore") as fd:
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


def shift_subtitle_timeline_srt(input_subtitle_path, shift_second):
    # 输入字幕路径
    if input_subtitle_path == 0:
        input_subtitle_path = input("请输入字幕文件路径：").replace('"', "")
    input_subtitle_name = input_subtitle_path.split("\\")[-1]
    input_subtitle_format = input_subtitle_name.split(".")[-1]
    # 确认字幕移动时间数值
    if shift_second == 0:
        shift_second = float(
            input("请输字幕时间线移动数值，正整数为向后移动，负整数为向前移：")
        )
    # 获取字幕内容
    try:
        with open(input_subtitle_path, "r", encoding="UTF-8") as f:
            subtitle_data = f.readlines()
    except UnicodeDecodeError:
        detect_and_convert_encoding(input_subtitle_path)
        with open(input_subtitle_path, "r", encoding="UTF-8") as f:
            subtitle_data = f.readlines()
    # 提取时间点并修改
    for line in subtitle_data:
        if "-->" in line:
            where = subtitle_data.index(line)  # 标记索引
            start, end = line.split(" --> ")  # 开始结束时间
            start_h, start_m, start_s, start_ms = re.split(r"[:,.]", start)  # 开始时间
            end_h, end_m, end_s, end_ms = re.split(r"[:,.]", end)  # 结束时间
            start_total_ms = (
                int(start_h) * 3600000
                + int(start_m) * 60000
                + int(start_s) * 1000
                + int(start_ms)
            )
            end_total_ms = (
                int(end_h) * 3600000
                + int(end_m) * 60000
                + int(end_s) * 1000
                + int(end_ms)
            )
            if start_total_ms + shift_second >= 0:
                start_total_ms = (
                    start_total_ms + shift_second
                )  # 添加了移动时间的开始时间
                end_total_ms = end_total_ms + shift_second  # 添加了移动时间的结束时间
            start_h, remain = divmod(
                start_total_ms, 3600000
            )  # 将开始时间转回时、分、秒、毫秒
            start_m, remain = divmod(remain, 60000)
            start_s, remain = divmod(remain, 1000)
            start_ms = remain
            end_h, remain = divmod(
                end_total_ms, 3600000
            )  # 将开始时间转回时、分、秒、毫秒
            end_m, remain = divmod(remain, 60000)
            end_s, remain = divmod(remain, 1000)
            end_ms = remain
            if input_subtitle_format == "srt":
                start = f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d}"
                end = f"{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}"  # 将结束时间换回00:00:00,000格式
            elif input_subtitle_format == "vtt":
                start = f"{start_h:02d}:{start_m:02d}:{start_s:02d}.{start_ms:03d}"
                end = f"{end_h:02d}:{end_m:02d}:{end_s:02d}.{end_ms:03d}"  # 将结束时间换回00:00:00,000格式
            line = start + " --> " + end + "\n"
            subtitle_data[where] = line
    with open(input_subtitle_path, "w", encoding="UTF-8") as f:
        for line in subtitle_data:
            f.write(line)
    print(f"{input_subtitle_path}修改成功")


def shift_subtitle_timeline_ass(input_subtitle_path, shift_second):
    # 输入字幕路径
    if input_subtitle_path == 0:
        input_subtitle_path = input("请输入字幕文件路径：").replace('"', "")
    input_subtitle_name = input_subtitle_path.split("\\")[-1]
    input_subtitle_format = input_subtitle_name.split(".")[-1]
    # 确认字幕移动时间数值
    if shift_second == 0:
        shift_second = float(
            input("请输字幕时间线移动数值，正整数为向后移动，负整数为向前移：")
        )
    # 获取字幕内容
    try:
        with open(input_subtitle_path, "r", encoding="UTF-8") as f:
            subtitle_data = f.readlines()
    except UnicodeDecodeError:
        detect_and_convert_encoding(input_subtitle_path)
        with open(input_subtitle_path, "r", encoding="UTF-8") as f:
            subtitle_data = f.readlines()
    # 提取时间点并修改
    for line in subtitle_data:
        if "Dialogue" in line:
            where = subtitle_data.index(line)  # 标记索引
            # line = line.replace('\n', '')  # 去掉换行符
            start, end = re.findall("(\d+:\d+:\d+\.\d+)", line)  # 开始结束时间
            old_time = f"{start},{end}"
            start_h, start_m, start_s, start_ms = re.split(r"[:.]", start)  # 开始时间
            end_h, end_m, end_s, end_ms = re.split(r"[:.]", end)  # 结束时间
            start_ms = float(f"0.{start_ms}") * 1000
            end_ms = float(f"0.{end_ms}") * 1000
            start_total_ms = (
                int(start_h) * 3600000
                + int(start_m) * 60000
                + int(start_s) * 1000
                + int(start_ms)
            )
            end_total_ms = (
                int(end_h) * 3600000
                + int(end_m) * 60000
                + int(end_s) * 1000
                + int(end_ms)
            )
            if start_total_ms + shift_second >= 0:
                start_total_ms = (
                    start_total_ms + shift_second
                )  # 添加了移动时间的开始时间
                end_total_ms = end_total_ms + shift_second  # 添加了移动时间的结束时间
            start_h, remain = divmod(
                start_total_ms, 3600000
            )  # 将开始时间转回时、分、秒、毫秒
            start_m, remain = divmod(remain, 60000)
            start_s, remain = divmod(remain, 1000)
            start_ms = int(remain / 10)
            end_h, remain = divmod(
                end_total_ms, 3600000
            )  # 将开始时间转回时、分、秒、毫秒
            end_m, remain = divmod(remain, 60000)
            end_s, remain = divmod(remain, 1000)
            end_ms = int(remain / 10)
            if input_subtitle_format == "srt":
                start = f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:02d}"
                end = f"{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}"  # 将结束时间换回00:00:00,000格式
            elif input_subtitle_format == "ass":
                start = f"{start_h:02d}:{start_m:02d}:{start_s:02d}.{start_ms:02d}"
                end = f"{end_h:02d}:{end_m:02d}:{end_s:02d}.{end_ms:02d}"  # 将结束时间换回00:00:00,000格式
            new_time = f"{start},{end}"
            line = line.replace(old_time, new_time)
            subtitle_data[where] = line
    with open(input_subtitle_path, "w", encoding="UTF-8") as f:
        for line in subtitle_data:
            f.write(line)
    print(f"{input_subtitle_path}修改成功")


if __name__ == "__main__":
    folder_path = pyperclip.paste()
    time_delay = 50
    if os.path.isdir(folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".ass"):
                    file_path = os.path.join(root, file)
                    shift_subtitle_timeline_ass(file_path, time_delay)
                elif file.endswith(".srt"):
                    file_path = os.path.join(root, file)
                    shift_subtitle_timeline_srt(file_path, time_delay)
    else:
        file_path = folder_path
        if file_path.endswith(".ass"):
            shift_subtitle_timeline_ass(file_path, time_delay)
        elif file_path.endswith(".srt"):
            shift_subtitle_timeline_srt(file_path, time_delay)
