import os
import requests

# 设置 TMDb API 密钥
api_key = "896c4c7d5af3899b0f56be6824560848"


def extract_show_info(folder_name):
    """从文件夹名中提取剧集名称和年份"""
    try:
        show_name, show_year = folder_name.split(" (")
        show_year = show_year[:-1]
        return show_name, show_year
    except (ValueError, IndexError):
        print(f"Error extracting show info from folder name: {folder_name}")
        return None, None


def search_tmdb(show_name, show_year):
    """使用 TMDb API 搜索剧集"""
    try:
        search_url = f"https://api.themoviedb.org/3/search/tv?api_key={api_key}&query={show_name}"
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        for result in data["results"]:
            if str(result["first_air_date"]).startswith(show_year):
                return result["id"]
    except (requests.exceptions.RequestException, KeyError):
        print(f'Error searching TMDb for "{show_name} ({show_year})"')
    return None


def rename_folder(folder_path, folder_name, tmdb_id):
    global num
    """重命名文件夹"""
    try:
        new_folder_name = f"{folder_name} {{tmdb-{tmdb_id}}}"
        new_folder_path = os.path.join(folder_path, new_folder_name)
        os.rename(os.path.join(folder_path, folder_name), new_folder_path)
        num += 1
        print(f"Folder renamed: {folder_name} -> {new_folder_name} {num}")
    except OSError as e:
        print(f"Error renaming folder {folder_name}: {e}")


def process_folder(folder_path, folder_name):
    """处理单个文件夹"""
    # 跳过包含 "tmdb" 的文件夹
    if "tmdb" in folder_name.lower():
        return

    show_name, show_year = extract_show_info(folder_name)
    if show_name is None or show_year is None:
        return

    tmdb_id = search_tmdb(show_name, show_year)
    if tmdb_id:
        rename_folder(folder_path, folder_name, tmdb_id)
    else:
        print(f"No match found for: {folder_name}")


def main(folder_path):
    """主函数"""
    for folder_name in os.listdir(folder_path):
        process_folder(folder_path, folder_name)


if __name__ == "__main__":
    num = 0
    dir_list = [
        "/Users/shenxian/CloudNAS/CloudDrive2/115(devdong)/我的接收/MYTVSUPER/MYTVSUPER_1",
        "/Users/shenxian/CloudNAS/CloudDrive2/115(devdong)/我的接收/MYTVSUPER/MYTVSUPER_2",
        "/Users/shenxian/CloudNAS/CloudDrive2/115(devdong)/我的接收/MYTVSUPER/MYTVSUPER_3",
        "/Users/shenxian/CloudNAS/CloudDrive2/115(devdong)/我的接收/MYTVSUPER/MYTVSUPER_4",
        "/Users/shenxian/CloudNAS/CloudDrive2/115(devdong)/我的接收/MYTVSUPER/MYTVSUPER_5",
    ]
    for dir in dir_list:
        # 使用示例
        main(dir)
