import json
import subprocess
import os
import traceback

working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)


def write_completed_file_name(file_path):
    with open("completed_file_name.txt", "a", encoding="utf-8") as f:
        f.write(f"{file_path}\n")


def write_video_without_chs(file_path):
    with open("video_without_chs.txt", "a", encoding="utf-8") as f:
        f.write(f"{file_path}\n")


def get_chinese_sub_dict(video_path=None):
    chi_flag = False
    try:
        subtitles = get_subtitle_info(video_path)
        for sub_dict in subtitles:
            title = sub_dict["title"]
            if "简" in title or "sim" in title.lower() or "chs" in title.lower():
                print(f"{video_path}::: {title}")
                chi_flag = True
                break
        if not chi_flag:
            write_video_without_chs(video_path)
            print(f"该视频不包含中文简体字幕::: {video_path}")
        write_completed_file_name(video_path)
    except:
        print(traceback.format_exc())


def get_subtitle_info(video_path):
    # 运行ffprobe命令并捕获输出
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        "-select_streams",
        "s",
        video_path,
    ]
    output = subprocess.check_output(command)

    # 解析输出的JSON数据
    data = json.loads(output)

    # 提取字幕信息
    subtitles = []
    for stream in data["streams"]:
        if stream["codec_type"] == "subtitle":
            language = stream.get("tags", {}).get("language", "")
            title = stream.get("tags", {}).get("title", "")
            index = str(int(stream["index"]) - 2)
            format_name = stream["codec_name"]
            subtitles.append(
                {
                    "language": language,
                    "title": title,
                    "index": index,
                    "format": format_name,
                }
            )
    return subtitles


if __name__ == "__main__":
    with open("completed_file_name.txt", "r", encoding="utf-8") as f:
        video_list = f.read().strip().split("\n")

    video_num = 0
    folder_list = [
        "/Users/shenxian/CloudNAS/CloudDrive2/115/看剧/Nas/电影合集/华语电影",
    ]
    video_extensions = (
        ".mkv",
        ".iso",
        ".ts",
        ".mp4",
        ".avi",
        ".rmvb",
        ".wmv",
        ".m2ts",
        ".mpg",
        ".flv",
        ".rm",
        ".mov",
    )
    for folder_path in folder_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(video_extensions):
                    file_path = os.path.join(root, file)
                    video_num += 1
                    if file_path not in video_list:
                        get_chinese_sub_dict(file_path)
                    print(f"已处理{video_num}个视频文件.")
