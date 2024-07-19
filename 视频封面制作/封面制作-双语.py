from PIL import Image, ImageDraw, ImageFont
import os, re

working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)


def crop_and_draw_text(image_path, text, eng_text, font_size_ratio=0.2):
    # 保存处理后的图像
    image_dir = os.path.dirname(image_path)
    _, ext = os.path.splitext(image_path)
    output_path = os.path.join(image_dir, f"{text}-封面{ext}")
    # if os.path.exists(output_path):
    #     return
    # 打开图像
    image = Image.open(image_path)
    eng_text = eng_text
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

    width, height = image.size
    new_width = 960
    new_height = int(new_width * height / width)

    # 调整图片大小
    image = image.resize((new_width, new_height))
    width, height = image.size

    draw = ImageDraw.Draw(image)

    # 计算字体大小
    font_size = int(height * font_size_ratio)
    eng_font_size = int(font_size / 2)
    eng_font = font = ImageFont.truetype(
        "点字倔强黑.ttf",
        eng_font_size,
    )  # 可替换为您喜欢的字体和大小
    font = ImageFont.truetype(
        "方正综艺简体.ttf",
        font_size,
    )  # 可替换为您喜欢的字体和大小

    eng_text_color = (0, 0, 0)  # 黑色

    text_color = (255, 255, 255)  # 白色
    shadow_color = (0, 0, 0)  # 黑色
    shadow_offset = (5, 5)  # 阴影偏移量

    # 计算文本宽度和高度
    bbox = draw.textbbox((0, 0), eng_text, font=eng_font)
    eng_text_width = bbox[2] - bbox[0]
    eng_text_height = bbox[3] - bbox[1]

    # 创建一个纯白色的图像
    white_height = eng_text_height + 20
    white_image = Image.new("RGB", (image.width, white_height), (255, 255, 255))

    eng_text_position = (
        (image.width - eng_text_width) // 2,
        image.height - white_height + (white_height - eng_text_height) // 2 - 15,
    )

    # 将白色图像粘贴到指定区域
    image.paste(white_image, (0, image.height - white_height))

    print(image.height, white_height, eng_text_height, eng_text_position)
    bbox = draw.textbbox((0, 0), text, font=eng_font)
    # 计算文本宽度和高度
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # # 确定文本位置
    # text_position = (
    #     (image.width - text_width) // 2,
    #     image.height - text_height - eng_text_height - 30,
    # )

    # 确定文本位置
    text_position = (
        35,
        image.height - text_height - eng_text_height - 100,
    )
    # 绘制阴影
    shadow_position = (
        text_position[0] + shadow_offset[0],
        text_position[1] + shadow_offset[1],
    )
    text = add_spaces_between_strings(text)
    draw.text(shadow_position, text, font=font, fill=shadow_color)

    # 绘制文本
    draw.text(eng_text_position, eng_text, font=eng_font, fill=eng_text_color)
    draw.text(text_position, text, font=font, fill=text_color)

    image.save(output_path)

    # 显示处理后的图像
    # image.show()


def add_spaces_between_strings(input_string):
    # 使用正则表达式在相邻的中文字符之间插入空格
    # result = re.sub(r"(?<=\S)(?=\S)", " ", input_string)
    print(input_string)
    result = re.sub(r"([\u4e00-\u9fff])", "\\1 ", input_string)
    return result


cover_list = {
    "观影": "Movies",
    "追剧": "Tv Shows",
    "日剧": "Japan Dramas",
    "韩剧": "Korea Dramas",
    "国产剧": "China Dramas",
    "欧美剧": "Western Dramas",
    "华语电影": "China Movies",
    "欧美电影": "Western Movies",
    "日韩电影": "Japan Korea Movies",
    "动画电影": "Anime Movies",
    "蓝光电影": "BlueRay Movies",
    "周星驰系列": "Stephen Chou",
    "日漫": "Japan Anime",
    "国漫": "China Anime",
    "儿童动漫": "Children Anime",
    "纪录片": "Documentries",
    "电视剧集": "Tv Shows",
    "动画片": "Anime Shows",
    "动漫": "Japan Anime",
    "国外电影": "Foreign Movies",
    "韩国": "Korea Media",
    "中国": "China Media",
    "综艺": "Varieties",
    "音乐": "Music",
    "4K REMUX": "4K REMUX",
    "Top 250": "Top 250",
}

image_dir = "/Users/shenxian/Downloads/封面"
font_size_ratio = 0.2
for file in os.listdir(image_dir):
    filename, _ = os.path.splitext(file)
    if (
        not file.endswith((".png", ".jpg", ".jpeg"))
        or filename not in cover_list.keys()
    ):
        continue
    image_path = os.path.join(image_dir, file)
    text = filename
    eng_text = cover_list[filename]
    crop_and_draw_text(image_path, text, eng_text, font_size_ratio)
