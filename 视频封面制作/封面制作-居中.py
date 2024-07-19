from PIL import Image, ImageDraw, ImageFont
import os, re


def crop_and_draw_text(image_path, text, font_size_ratio):
    # 保存处理后的图像
    image_dir = os.path.dirname(image_path)
    _, ext = os.path.splitext(image_path)
    output_path = os.path.join(image_dir, f"{text}{ext}")
    # 打开图像
    image = Image.open(image_path)

    # 裁剪图像为16:9的比例
    width, height = image.size
    target_ratio = 16 / 9
    current_ratio = width / height
    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        right = left + new_width
        image = image.crop((left, 0, right, height))
    elif current_ratio < target_ratio:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        image = image.crop((0, top, width, bottom))

    new_width = 960
    new_height = int(new_width * height / width)

    # 调整图片大小
    image = image.resize((new_width, new_height))
    width, height = image.size

    draw = ImageDraw.Draw(image)

    # 计算字体大小
    font_size = int(height * font_size_ratio)
    font = ImageFont.truetype(
        "方正综艺简体.ttf",
        font_size,
    )  # 可替换为您喜欢的字体和大小
    text_color = (255, 255, 255)  # 白色
    shadow_color = (0, 0, 0)  # 黑色
    shadow_offset = (5, 5)  # 阴影偏移量

    # 计算文本宽度和高度
    text_width, text_height = draw.textsize(text, font=font)

    # 确定文本位置
    text_position = ((image.width - text_width) // 2, image.height - text_height - 60)

    # 绘制阴影
    shadow_position = (
        text_position[0] + shadow_offset[0],
        text_position[1] + shadow_offset[1],
    )
    text = add_spaces_between_strings(text)
    # draw.text(shadow_position, text, font=font, fill=shadow_color)

    # 绘制文本
    draw.text(text_position, text, font=font, fill=text_color)

    image.save(output_path)

    # 显示处理后的图像
    image.show()


def add_spaces_between_strings(input_string):
    # 使用正则表达式在相邻的中文字符之间插入空格
    result = re.sub(r"(?<=\S)(?=\S)", " ", input_string)
    return result


# 示例用法
input_path = "/Users/shenxian/Downloads/1.jpeg,韩剧"
font_size_ratio = 0.2
image_path, text = input_path.split(",")
crop_and_draw_text(image_path, text, font_size_ratio)
