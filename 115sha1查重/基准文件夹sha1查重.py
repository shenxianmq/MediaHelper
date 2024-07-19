import os
from clouddrive import CloudDriveClient, CloudDriveFileSystem
import configparser

working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)


class BaseFolderDuplicateFileFinder:
    def __init__(self):
        self.clouddrvie2_address = ""
        self.clouddrive2_account = ""
        self.clouddrive2_passwd = ""
        self.base_folder = ""
        self.target_folder = ""
        self.clouddrive2_root_path = ""
        self.fs = ""

    def set_config(
        self,
        clouddrvie2_address,
        clouddrive2_account,
        clouddrive2_passwd,
        base_folder,
        target_folder,
        clouddrive2_root_path,
    ):
        self.clouddrvie2_address = clouddrvie2_address
        self.clouddrive2_account = clouddrive2_account
        self.clouddrive2_passwd = clouddrive2_passwd
        self.base_folder = base_folder
        self.target_folder = target_folder
        self.clouddrive2_root_path = clouddrive2_root_path
        client = CloudDriveClient(
            clouddrvie2_address, clouddrive2_account, clouddrive2_passwd
        )
        self.fs = CloudDriveFileSystem(client)

    def find_duplicate_files(self):
        hash_map = self.get_base_folder_hash_list()
        duplicate_files = []
        fs_dir_path = self.target_folder.replace(self.clouddrive2_root_path, "")
        for foldername, subfolders, filenames in self.fs.walk_path(fs_dir_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in [
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
                ]:
                    file_sha1 = self.fs.attr(file_path)["fileHashes"]["2"]
                    print(file_path)
                    if file_sha1 in hash_map:
                        duplicate_files.append((hash_map[file_sha1], file_path))
                        try:
                            self.fs.remove(file_path)
                        except:
                            pass
                        print(f"已经删除sha1重复的文件::: {file_path}")
        return duplicate_files

    def get_base_folder_hash_list(self):
        hash_map = {}
        fs_dir_path = self.base_folder.replace(self.clouddrive2_root_path, "")
        for foldername, subfolders, filenames in self.fs.walk_path(fs_dir_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in [
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
                ]:
                    file_sha1 = self.fs.attr(file_path)["fileHashes"]["2"]
                    if file_sha1 not in hash_map:
                        hash_map[file_sha1] = file_path
                        print(file_path)
        return hash_map

    def write_results_to_file(self, results, output_file):
        with open(output_file, "w") as f:
            for duplicate_pair in results:
                f.write("Duplicate files:\n")
                f.write(f"{duplicate_pair[0]}\n")
                f.write(f"{duplicate_pair[1]}\n")
                f.write("\n")


if __name__ == "__main__":
    # 使用示例
    config_file_path = "config.ini"  # 你的配置文件路径
    config = configparser.ConfigParser()

    # 读取 INI 文件
    config.read(config_file_path)
    config = config["config"]

    clouddrvie2_address = config["clouddrvie2_address"]
    clouddrive2_account = config["clouddrive2_account"]
    clouddrive2_passwd = config["clouddrive2_passwd"]
    root_path = config["root_path"]
    base_folder = config["base_folder"]
    target_folder = config["target_folder"]
    clouddrive2_root_path = config["clouddrive2_root_path"]

    base_finder = BaseFolderDuplicateFileFinder()
    base_finder.set_config(
        clouddrvie2_address,
        clouddrive2_account,
        clouddrive2_passwd,
        base_folder,
        target_folder,
        clouddrive2_root_path,
    )
    duplicate_files = base_finder.find_duplicate_files()
    # output_file = "/Users/shenxian/Desktop/res.txt"
    # finder.write_results_to_file(duplicate_files, output_file)
    # print("Duplicate files found and written to:", output_file)
