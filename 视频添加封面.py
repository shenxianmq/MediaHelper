import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import re
import math
import jieba


def extract_chinese(text):
    """提取第一个中文字符及之后的部分，并移除括号内的内容以及类似'10集'的字样"""
    text = re.sub(r"\（.*?\）|\(.*?\)", "", text)  # 移除括号及其内容，使用非贪婪模式
    text = re.sub(r"\d+集", "", text)  # 移除类似'10集'的字样
    for i, char in enumerate(text):
        if "\u4e00" <= char <= "\u9fff":
            return text[i:]
    return text


def calculate_font_size(
    image_height, text_length, shadow_offset, max_chars_per_column, margin
):
    """计算字体大小以使文字竖直排列时填满图片的高度，同时考虑阴影偏移量和边距"""
    # 减去阴影偏移量和边距以确保最后一个字符不超出图片边界
    return (image_height - shadow_offset - 2 * margin) // min(
        text_length, max_chars_per_column
    )


def calculate_columns(text, max_chars_per_column):
    """根据jieba分词结果计算列数"""
    words = jieba.lcut(text)
    columns = []
    column = ""
    for word in words:
        if len(column) + len(word) > max_chars_per_column:
            columns.append(column)
            column = word
        else:
            column += word
    if column:
        columns.append(column)
    return columns


# 文件夹路径
folder = "T:\\爆火短剧【10月·11月·12月】\\2024年1月"
font_path = "d:/ziti2.ttf"  # 字体文件路径
shadow_offset = 8  # 阴影偏移量
max_chars_per_column = 8  # 每列最多字符数
margin = 75  # 边距

for root, dirs, files in os.walk(folder):
    for dir in dirs:
        dir_path = os.path.join(root, dir)
        print(f"Checking directory: {dir_path}")  # 打印当前检查的目录

        jpg_files = [f for f in os.listdir(dir_path) if f.endswith(".jpg")]
        if jpg_files:
            source_file = os.path.join(dir_path, jpg_files[0])
            destination_file = os.path.join(dir_path, "poster.jpg")

            # 如果poster.jpg存在，则删除
            if os.path.exists(destination_file):
                os.remove(destination_file)
                # 重新获取jpg文件列表
                jpg_files = [f for f in os.listdir(dir_path) if f.endswith(".jpg")]
                if not jpg_files:
                    print(f"No .jpg files found in {dir_path}")
                    continue
                source_file = os.path.join(dir_path, jpg_files[0])

            try:
                shutil.copy2(source_file, destination_file)

                # 打开图片
                image = Image.open(destination_file)
                image_width, image_height = image.size

                # 提取文字
                text = extract_chinese(dir)

                # 计算列数
                columns = calculate_columns(text, max_chars_per_column)
                num_columns = len(columns)

                # 计算字体大小
                font_size = calculate_font_size(
                    image_height, len(text), shadow_offset, max_chars_per_column, margin
                )
                font = ImageFont.truetype(font_path, font_size)

                draw = ImageDraw.Draw(image)

                # 竖直排列文字
                text_position_x = 50  # 文字起始横坐标，可以根据需要调整
                for i, column in enumerate(columns):
                    for j, char in enumerate(column):
                        text_position_y = margin + j * font_size  # 每个字符的纵坐标
                        text_position_x = 50 + i * (
                            font_size + shadow_offset
                        )  # 每个字符的横坐标

                        # 绘制阴影
                        draw.text(
                            (
                                text_position_x + shadow_offset,
                                text_position_y + shadow_offset,
                            ),
                            char,
                            font=font,
                            fill=(0, 0, 0),
                        )  # 阴影颜色为黑色

                        # 绘制文字
                        draw.text(
                            (text_position_x, text_position_y),
                            char,
                            font=font,
                            fill=(255, 255, 255),
                        )  # 文字颜色为白色

                # 保存图片
                image.save(destination_file)

                print(f"Processed and saved {destination_file}")
            except Exception as e:
                print(f"Error processing {source_file}: {e}")
        else:
            print(f"No .jpg files found in {dir_path}")
