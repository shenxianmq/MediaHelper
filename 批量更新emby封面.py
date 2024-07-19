import requests
import os
import base64


# 定义 Emby 服务器信息
EMBY_SERVER = "http://192.168.9.28:8096"
EMBY_API_KEY = "d0ef77bc3905408381b15c38d12a7ffc"

# 定义媒体库名称和对应的封面图片映射
cover_mapping = {
    "儿童动漫": "儿童动漫-封面.jpeg",
    "观影": "观影-封面.jpg",
    "国产剧": "国产剧-封面.jpeg",
    "国漫": "国漫-封面.jpeg",
    "韩剧": "韩剧-封面.jpeg",
    "华语电影": "华语电影-封面.jpeg",
    "纪录片": "纪录片-封面.jpeg",
    "蓝光电影": "蓝光电影-封面.jpeg",
    "欧美电影": "欧美电影-封面.jpeg",
    "欧美剧": "欧美剧-封面.jpeg",
    "日韩电影": "日韩电影-封面.jpeg",
    "日剧": "日剧-封面.jpeg",
    "日漫": "日漫-封面.jpeg",
    "音乐": "音乐-封面.png",
    "周星驰系列": "周星驰系列-封面.jpeg",
    "追剧": "追剧-封面.jpg",
    "4K Remux": "4K Remux-封面.jpg",
}

# 定义封面图片所在的文件夹路径
COVER_FOLDER_PATH = "/Users/shenxian/沈闲云/沈闲/封面/emby封面"


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode()
    return base64_image


# 获取媒体库列表
def get_media_libraries():
    url = f"{EMBY_SERVER}/emby/Library/SelectableMediaFolders?api_key={EMBY_API_KEY}"
    response = requests.get(url)
    return response.json()


# 更新媒体库封面
def update_library_cover(library_id, cover_file):
    url = f"{EMBY_SERVER}/emby/Items/{library_id}/Images/Primary?api_key={EMBY_API_KEY}"

    # 将图片转换为Base64编码
    base64_image = image_to_base64(os.path.join(COVER_FOLDER_PATH, cover_file))
    headers = {"Content-Type": "image/jpg"}
    response = requests.post(url, data=base64_image, headers=headers)
    return response.status_code


# 主函数
def main():
    # 获取媒体库列表
    media_libraries = get_media_libraries()

    # 遍历媒体库并更新封面
    for library in media_libraries:
        library_name = library["Name"]
        library_id = library["Id"]

        # 检查是否有对应的封面图片
        if library_name in cover_mapping:
            cover_file = cover_mapping[library_name]
            print(f"开始为媒体库 '{library_name}' 更新封面...")
            status_code = update_library_cover(library_id, cover_file)
            if status_code == 204:
                print(f"媒体库 {library_name} 成功更新封面\n")
            else:
                print(f"媒体库 {library_name} 更新封面失败,状态码: {status_code}\n")
        else:
            print(f"没有找到媒体库 '{library_name}' 的封面\n")


if __name__ == "__main__":
    main()
