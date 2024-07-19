import requests

# 配置Emby服务器信息
EMBY_SERVER_URL = "http://192.168.9.89:8096"
API_KEY = ""
# 如果电影文件的实际路径带有下列某个字符串,则跳过合并,以;隔开
exclude_str = "Remux - 特效字幕;"

import time


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        print(f"总耗时: {total_time:.2f} 秒")
        return result

    return wrapper


# 获取所有电影的信息
def get_all_movies():
    url = f"{EMBY_SERVER_URL}/emby/Items"
    params = {
        "api_key": API_KEY,
        "IncludeItemTypes": "Movie",
        "Recursive": True,
        "Fields": "ProviderIds,Path",
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()["Items"]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # 输出HTTP错误
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")  # 输出其他错误
    except ValueError:
        print("Error parsing JSON response")
        print("Response content:", response.content)  # 输出响应内容以便调试
    return []


# 按照TMDb ID分组
def group_movies_by_tmdbid(movies):
    grouped_movies = {}
    if ";" in exclude_str:
        exclude_list = exclude_str.split(";")
        exclude_list = [item for item in exclude_list if len(item) > 0]
    else:
        exclude_list = [exclude_str]
    for movie in movies:
        tmdb_id = movie.get("ProviderIds", {}).get("Tmdb", "")
        file_path = movie.get("Path", "")
        if any(item in file_path for item in exclude_list):
            continue
        if tmdb_id:
            if tmdb_id not in grouped_movies:
                grouped_movies[tmdb_id] = []
            grouped_movies[tmdb_id].append(movie)
    return grouped_movies


# 合并同一个TMDb ID下的不同版本
@measure_time
def merge_movie_versions(grouped_movies):
    merged_movies = []
    for tmdb_id, movies in grouped_movies.items():
        if len(movies) > 1:
            name = movies[0]["Name"]
            print(f"已发现相同版本的电影::: {name} \n")
            # for movie in movies:
            #     print(f" - {movie['Name']} ({movie['Id']})")
            # 调用Emby API进行合并
            item_ids = ",".join(movie["Id"] for movie in movies)
            merge_url = f"{EMBY_SERVER_URL}/emby/Videos/MergeVersions"
            payload = {
                "Ids": item_ids,
                "X-Emby-Token": API_KEY,
            }
            print(f"合并版本成功::: {name}\n")
            response = requests.post(merge_url, params=payload)
            if response.status_code == 204:
                print(f"合并版本成功::: {name}")
            else:
                print(f"合并版本失败::: {name}")
            merged_movies.append(movies[0])  # 暂时保留第一部电影为合并结果
    return merged_movies


# 主函数
def main():
    all_movies = get_all_movies()
    if not all_movies:
        print("没有多版本的电影")
        return
    grouped_movies = group_movies_by_tmdbid(all_movies)
    merged_movies = merge_movie_versions(grouped_movies)
    print(f"共合并电影数: {len(merged_movies)}")


if __name__ == "__main__":
    main()
