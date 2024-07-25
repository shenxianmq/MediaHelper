#!/usr/bin/env python3

import os
import subprocess
import re
import requests
import json
import platform

# DOMAIN_HOST=1 to enable, 0 to disable custom domain hosts file writing
# GITHUB_HOST=1 to enable, 0 to disable GitHub domain hosts file writing
DOMAIN_HOST = 1
GITHUB_HOST = 0

# List of custom domains, separated by spaces
DOMAIN_LIST = ["api.themoviedb.org", "image.tmdb.org"]

GITHUB_HOST_URL = "https://hosts.gitcdn.top/hosts.txt"
DNS_API = "https://networkcalc.com/api/dns/lookup"


def get_hosts_file_path():
    system = platform.system()
    if system == "Windows":
        return r"C:\Windows\System32\drivers\etc\hosts"
    elif system == "Darwin":
        return "/etc/hosts"
    elif system == "Linux":
        return "/etc/hosts"
    else:
        raise Exception("Unsupported operating system")


HOSTS_PATH = get_hosts_file_path()


def parse_dns_response(response_json):
    """
    解析 DNS 查询的 JSON 响应,返回 IP 地址列表.

    Args:
        response_json (str): 包含 DNS 查询结果的 JSON 字符串.

    Returns:
        list: 包含所有 A 记录 IP 地址的列表.
    """
    try:
        # 解析 JSON 字符串为 Python 字典
        response_data = json.loads(response_json)

        # 检查响应状态是否为 "OK"
        if response_data["status"] != "OK":
            return []

        # 提取 A 记录中的所有 IP 地址
        ip_addresses = [record["address"] for record in response_data["records"]["A"]]

        return ip_addresses

    except (KeyError, ValueError):
        # 如果 JSON 解析或访问字典键失败,返回空列表
        return []


def update_tmdb_host():
    with open(HOSTS_PATH, "r") as hosts_file:
        hosts_content = hosts_file.read()

    # 删除之前的内容
    new_content = re.sub(
        r"# tmdb-domain-hosts begin.*?# tmdb-domain-hosts end\n",
        "",
        hosts_content,
        flags=re.DOTALL,
    )

    # 写入新的内容
    with open(HOSTS_PATH, "w") as hosts_file:
        hosts_file.write(new_content)
        hosts_file.write("# tmdb-domain-hosts begin\n")
        for domain in DOMAIN_LIST:
            try:
                response = requests.get(f"{DNS_API}/{domain}")
                domain_ip_list = parse_dns_response(response.text)
                for domain_ip in domain_ip_list:
                    hosts_file.write(f"{domain_ip}\t\t{domain}\n")
            except requests.exceptions.RequestException:
                pass
        hosts_file.write("# tmdb-domain-hosts end\n")


update_tmdb_host()
