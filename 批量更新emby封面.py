import requests
import os
import base64


class EmbyCoverUpdater:
    def __init__(self, server, api_key, cover_folder_path):
        self.server = server
        self.api_key = api_key
        self.cover_folder_path = cover_folder_path

    def image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode()
        return base64_image

    def get_image_list(self):
        image_list = []
        for root, dirs, files in os.walk(self.cover_folder_path):
            for file in files:
                if file.lower().endswith((".jpg", "jpeg", ".png", ".gif")):
                    file_path = os.path.join(root, file)
                    image_list.append(file_path)
        return image_list

    def get_media_libraries(self):
        url = (
            f"{self.server}/emby/Library/SelectableMediaFolders?api_key={self.api_key}"
        )
        response = requests.get(url)
        return response.json()

    def update_library_cover(self, library_id, library_name):
        image_list = self.get_image_list()
        image_path = None
        for file_path in image_list:
            filename = os.path.split(file_path)[-1]
            if library_name in filename:
                image_path = file_path
                break
        if image_path:
            try:
                url = f"{self.server}/emby/Items/{library_id}/Images/Primary?api_key={self.api_key}"
                base64_image = self.image_to_base64(image_path)
                headers = {"Content-Type": "image/jpg"}
                response = requests.post(url, data=base64_image, headers=headers)
                return response.status_code
            except:
                return 404
        else:
            return "未找到封面图片"

    def update_all_covers(self):
        media_libraries = self.get_media_libraries()
        for library in media_libraries:
            library_name = library["Name"]
            library_id = library["Id"]
            print(f"开始为媒体库 '{library_name}' 更新封面...")
            status_code = self.update_library_cover(library_id, library_name)
            if status_code == 204:
                print(f"媒体库 {library_name} 成功更新封面\n")
            else:
                print(f"媒体库 {library_name} 更新封面失败: {status_code}\n")


if __name__ == "__main__":
    EMBY_SERVER = "http://192.168.9.28:8096"
    EMBY_API_KEY = "d0ef77bc3905408381b15c38d12a7ffc"
    COVER_FOLDER_PATH = "/Users/shenxian/沈闲云/沈闲/封面/Emby封面"

    updater = EmbyCoverUpdater(EMBY_SERVER, EMBY_API_KEY, COVER_FOLDER_PATH)
    updater.update_all_covers()
