import requests
import logging
import os

working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)

# 创建日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s\n", "%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(console_format)

# 创建文件处理器
file_handler = logging.FileHandler("emby_extract.log")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s\n", "%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_format)

# 将处理器添加到记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

import time


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"总耗时: {total_time:.2f} 秒")
        return result

    return wrapper


# 获取所有电影的信息
def get_all_movies():
    url = f"{EMBY_SERVER_URL}/emby/Items"
    params = {
        "api_key": API_KEY,
        "IncludeItemTypes": "Movie,Episode",
        "Recursive": True,
        "Fields": "ProviderIds,Path",
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()["Items"]
    except requests.exceptions.HTTPError as http_err:
        logger.info(f"HTTP error occurred: {http_err}")  # 输出HTTP错误
    except requests.exceptions.RequestException as err:
        logger.info(f"Other error occurred: {err}")  # 输出其他错误
    except ValueError:
        logger.info("Error parsing JSON response")
        logger.info("Response content:", response.content)  # 输出响应内容以便调试
    return []


def scan_item(item_id: str):
    url = f"{EMBY_SERVER_URL}/emby/Items/{item_id}/PlaybackInfo"
    params = {
        "api_key": API_KEY,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return True
    else:
        logger.info(f"Request failed with status code: {response.status_code}")
        return False


# 主函数
def main():
    total_num = 0
    all_movies = get_all_movies()
    for item in all_movies:
        try:
            item_id = item["Id"]
            path = item["Path"]
            res = scan_item(item_id=item_id)
            if res:
                total_num += 1
                logger.info(f"已成功扫描片头信息:{path}\n共扫描{total_num}个视频")
        except:
            continue


if __name__ == "__main__":
    # 配置Emby服务器信息
    EMBY_SERVER_URL = "http://127.0.0.1:8096"
    API_KEY = "5b2d4062d9124a6ca9e7eab015251f53"
    main()
